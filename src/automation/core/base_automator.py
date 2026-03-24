# src/automation/core/base_automator.py
import re
import os
import time
import posixpath
import uiautomator2 as u2
from typing import Optional, List
from src.utils.logger import logger
import xml.etree.ElementTree as ET

class BaseAutomator:
    """
    Core automation class providing a wrapper for uiautomator2.
    
    This class handles device connection, background popup watchers,
    application lifecycle management, and logging synchronization with the UI.
    """
    def __init__(self, device_id: str, logger_signal=None):
        """
        Initializes the automator for a specific device.
        
        Args:
            device_id (str): The serial number or IP of the Android device.
            logger_signal (Optional[Signal]): PySide6 signal for emitting logs to the UI.
        """
        self.device_id = device_id
        self.logger_signal = logger_signal
        
        self.d = u2.connect(device_id)
        
        self._setup_watchers()
        self.pushed_files = []
        
    def _setup_watchers(self):
        """
        Registers background watchers using XPath to automatically handle common UI popups.
        
        Monitors for:
        1. Permission requests (Allow/Cho phép).
        2. Generic dismissals (Close/Skip/Later).
        3. Confirmation buttons (OK/Ok).
        """
        self.d.watcher("ALLOW_PERMISSION").when(
            "//android.widget.Button[contains(@text, 'Cho phép') or contains(@text, 'Allow') or contains(@text, 'CHO PHÉP')]"
        ).click()
        
        self.d.watcher("CLOSE_POPUP").when(
            "//android.widget.Button[contains(@text, 'Đóng') or contains(@text, 'Bỏ qua') or contains(@text, 'Lúc khác') or contains(@text, 'Close') or contains(@text, 'Skip') or contains(@text, 'Later')]"
        ).click()
        
        self.d.watcher("OK_BUTTON").when(
            "//android.widget.Button[@text='OK' or @text='Ok' or @text='ok']"
        ).click()

        self.d.watcher.start(interval=2.0)
        
    def log(self, message: str):
        """
        Synchronizes automation logs with the central logger and the UI status bar.
        
        Args:
            message (str): The log message to be displayed and recorded.
        """
        if self.logger_signal:
            self.logger_signal.emit(f"[{self.device_id}] {message}")
    
    def launch_app(self, package_name: str, deeplink: Optional[str] = None):
        """
        Starts an application, optionally navigating to a specific location via deep link.
        
        Args:
            package_name (str): The Android package name (e.g., 'com.facebook.katana').
            deeplink (Optional[str]): The deep link URL to trigger a specific activity.
        """
        self.disable_keyboard()
        if deeplink:
            self.log(f"Launching app via Deep Link: {deeplink}")
            cmd = f"am start -a android.intent.action.VIEW -d '{deeplink}' {package_name}"
            self.d.shell(cmd)
        else:
            self.log(f"Starting application normally...")
            self.d.app_start(package_name)

    def smart_sleep(self, seconds: int):
        """
        Performs a timed pause in execution.
        
        Args:
            seconds (int): Duration to sleep in seconds.
        """
        time.sleep(seconds)
    
    def get_user_media_path(self, user_id: int) -> str:
        """
        Determines the Virtual Path used by the Android Media Scanner and UI 
        based on the profile ID.

        Args:
            user_id (int): The Android user profile ID.

        Returns:
            str: The virtual path string.
        """
        if int(user_id) == 0:
            return "/sdcard/Pictures/PhoneFarm/"
        return f"/storage/emulated/{user_id}/Pictures/PhoneFarm/"
    
    def push_media(self, local_paths: List[str], user_id: int):
        """
        Pushes media files to the device by writing directly to the physical 
        storage (/data/media/) to bypass Multi-user permission restrictions.
        
        The process involves:
        1. Creating the physical directory with root privileges.
        2. Setting ownership to 'media_rw' so the Android OS can index the files.
        3. Pushing files via a temporary buffer to ensure integrity.
        4. Triggering a system broadcast to update the Media Store immediately.

        Args:
            local_paths (List[str]): List of local file paths to push.
            user_id (int): The target Android user profile ID.
        """
        virtual_dir = self.get_user_media_path(user_id)
        if not virtual_dir.endswith('/'):
            virtual_dir += '/'
            
        physical_dir = f"/data/media/{user_id}/Pictures/PhoneFarm/"
        
        self.d.shell(
            f"su -c 'mkdir -p \"{physical_dir}\" "
            f"&& chown media_rw:media_rw \"{physical_dir}\" "
            f"&& chmod 775 \"{physical_dir}\"'"
        )
        
        for local_path in local_paths:
            if not os.path.exists(local_path):
                self.log(f"⚠️ Local file not found: {local_path}")
                continue
                
            file_name = os.path.basename(local_path)
            virtual_path = posixpath.join(virtual_dir, file_name)
            physical_path = posixpath.join(physical_dir, file_name)
            tmp_path = posixpath.join("/data/local/tmp", file_name)
            
            try:
                self.d.push(local_path, tmp_path)
                
                copy_cmd = (
                    f"su -c 'cp -f \"{tmp_path}\" \"{physical_path}\" "
                    f"&& chown media_rw:media_rw \"{physical_path}\" "
                    f"&& chmod 664 \"{physical_path}\"'"
                )
                res_cp = self.d.shell(copy_cmd)
                
                if res_cp.exit_code != 0:
                    self.log(f"❌ Physical copy failed for {file_name}: {res_cp.output}")
                    continue
                    
                self.d.shell(f"rm \"{tmp_path}\"")
                
                self.pushed_files.append((virtual_path, user_id)) 
                
                target_user = user_id if int(user_id) != 0 else 0
                self.d.shell(
                    f"am broadcast --user {target_user} "
                    f"-a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
                    f"-d file://{virtual_path}"
                )
                
            except Exception as e:
                self.log(f"❌ Media push process error for {file_name}: {e}")
                
        self.log(f"📤 Successfully pushed {len(self.pushed_files)} files to device {self.device_id}")
    
    def verify_media_exists(self, local_paths: List[str], user_id: int) -> bool:
        """
        Verifies if the specified image or video files exist in the designated Android user's storage.

        This method checks the existence of remote files by mapping local filenames to the 
        expected remote paths for a specific Android user profile. It uses the shell 'ls' 
        command to confirm the presence of each file.

        Args:
            local_paths (List[str]): List of original local file paths (used to extract filenames).
            user_id (int): The Android user profile ID (e.g., 0, 10, 11).

        Returns:
            bool: True if ALL files exist on the device, False if at least one file is missing.
        """
        self.log(f"Verifying media data for User {user_id}...")
        
        remote_dir = self.get_user_media_path(user_id)
        if not remote_dir.endswith('/'):
            remote_dir += '/'
            
        all_exist = True
        
        for local_path in local_paths:
            file_name = os.path.basename(local_path)
            remote_path = posixpath.join(remote_dir, file_name)
            
            result = self.d.shell(f"ls '{remote_path}'")
            
            if result.exit_code == 0:
                self.log(f"✔️ Confirmed: {file_name} exists on device.")
            else:
                self.log(f"❌ MISSING FILE: {file_name} was not found in storage.")
                all_exist = False
                
        if all_exist:
            self.log("🎉 All media files verified successfully on the device!")
        else:
            self.log("⚠️ Warning: Some files were not pushed successfully.")
            
        return all_exist

    def cleanup_media(self):
        """
        Removes previously pushed media files from the device storage.
        
        This method utilizes Root privileges to delete physical files directly 
        from the /data/media/ partition, bypassing 'Permission Denied' errors 
        commonly encountered in Android Multi-user environments. It also 
        triggers the Media Scanner to remove the deleted entries from the 
        system gallery.
        """
        if not self.pushed_files:
            return
            
        self.log("Cleaning up pushed media files...")
        
        import os
        
        for virtual_path, user_id in self.pushed_files: 
            file_name = os.path.basename(virtual_path)
            
            # 1. Define physical path for direct root deletion
            physical_path = f"/data/media/{user_id}/Pictures/PhoneFarm/{file_name}"
            
            # 2. Execute physical deletion
            rm_cmd = f"rm -f \"{physical_path}\""
            if int(user_id) != 0:
                rm_cmd = f"su -c '{rm_cmd}'"
                
            self.d.shell(rm_cmd)
            
            # 3. Trigger Media Scanner to unregister the file from the Gallery
            target_user = user_id if int(user_id) != 0 else 0
            self.d.shell(
                f"am broadcast --user {target_user} "
                f"-a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
                f"-d file://{virtual_path}"
            )
            
        self.pushed_files.clear()
        self.log("✔️ Media cleanup complete. Device storage is now clean!")
        
    def teardown(self):
        """
        Performs resource cleanup after an automation job completes.
        """
        self.enable_keyboard()
        self.d.watcher.stop()
    
    def disable_keyboard(self):
        """
        Disables the Android soft keyboard by switching to uiautomator2's FastInputIME.
        """
        try:
            self.d.set_fastinput_ime(True)
            # self.log("⌨️ Soft keyboard disabled (FastInputIME activated).")
        except Exception as e:
            self.log(f"⚠️ Failed to disable keyboard: {e}")

    def enable_keyboard(self):
        """
        Restores the default Android soft keyboard.
        """
        try:
            self.d.set_fastinput_ime(False)
            # self.log("⌨️ Default soft keyboard restored.")
        except Exception as e:
            self.log(f"⚠️ Failed to restore keyboard: {e}")
    

    #===============================
    # ACTIONS
    #===============================

    def swipe_up(self, scale: float = 0.7):
        """
        Swipes the screen upward (simulating a finger sliding from bottom to top).
        """
        self.d.swipe_ext("up", scale=scale)
        self.smart_sleep(1)

    def swipe_down(self, scale: float = 0.7):
        """
        Swipes the screen downward (simulating a finger sliding from top to bottom).
        """
        self.d.swipe_ext("down", scale=scale)
        self.smart_sleep(1)

    def get_elements_by_widget(self, widget_class: str, timeout: int = 10):
        """
        Retrieves UI elements of a specific widget class, waiting for them to appear.
        """
        selector = self.d(className=widget_class)

        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if selector.exists:
                    return selector
                
                time.sleep(0.5)

        return selector
    
    def get_widget_by_text(self, class_name: str, text: str, exact: bool = False, timeout: int = 30):
        """
        Finds a specific Android widget by its class name using 'text' or 'content-desc' attributes.
        """
        safe_text = re.escape(text)
        text_pattern = f"(?i)^{safe_text}$" if exact else f"(?i).*{safe_text}.*"
        
        widget_text = self.d(className=class_name, textMatches=text_pattern)
        widget_desc = self.d(className=class_name, descriptionMatches=text_pattern)
        
        if exact:
            widget_native = self.d(className=class_name, text=text)
        else:
            widget_native = self.d(className=class_name, textContains=text)
        
        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if widget_text.exists: 
                    return widget_text
                if widget_desc.exists: 
                    return widget_desc
                if widget_native.exists: 
                    return widget_native
                
                time.sleep(0.5) 

        if widget_text.exists: 
            return widget_text
        if widget_desc.exists: 
            return widget_desc
        if widget_native.exists: 
            return widget_native
            
        return widget_text

    def get_button_by_text(self, text: str, exact: bool = False, timeout: int = 30):
        """
        Finds a Button or TextView based on either 'text' or 'content-desc' attributes.
        """
        safe_text = re.escape(text)
        text_pattern = f"(?i)^{safe_text}$" if exact else f"(?i).*{safe_text}.*"

        btn_text = self.d(className="android.widget.Button", textMatches=text_pattern, enabled=True)
        tv_text = self.d(className="android.widget.TextView", textMatches=text_pattern, enabled=True)
        
        btn_desc = self.d(className="android.widget.Button", descriptionMatches=text_pattern, enabled=True)
        tv_desc = self.d(className="android.widget.TextView", descriptionMatches=text_pattern, enabled=True)
        
        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if btn_text.exists: return btn_text
                if tv_text.exists: return tv_text
                if btn_desc.exists: return btn_desc
                if tv_desc.exists: return tv_desc
                
                time.sleep(0.5) 

        if btn_text.exists: return btn_text
        if tv_text.exists: return tv_text
        if btn_desc.exists: return btn_desc
        if tv_desc.exists: return tv_desc
            
        return btn_text
    
    def click_button_with_retry(
        self, 
        text: str, 
        max_retries: int = 3, 
        timeout: int = 15, 
        exact: bool = False, 
        wait_gone_timeout: int = 5
    ) -> bool:
        """
        Attempts to find and click a button, then waits for it to disappear.
        """
        for attempt in range(max_retries):
            btn = self.get_button_by_text(text, exact=exact, timeout=timeout)
            
            if not btn.exists:
                if attempt == 0:
                    return False
                else:
                    return True
            btn.click_exists(timeout=timeout)
            
            if btn.wait_gone(timeout=wait_gone_timeout):
                return True
                
        return False


    def get_interactable_from_parent(
        self, 
        parent_selector, 
        child_class: str = "android.view.ViewGroup", 
        text: str = "", 
        timeout: int = 30
    ):
        """
        Finds a child element within a parent container while ensuring script stability.
        """
        if not parent_selector.exists:
            return parent_selector 

        safe_text = re.escape(text)
        pattern = f"(?i).*{safe_text}.*"
        
        child_by_text = parent_selector.child(className=child_class, textMatches=pattern)
        child_by_desc = parent_selector.child(className=child_class, descriptionMatches=pattern)

        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if child_by_text.exists: 
                    return child_by_text
                if child_by_desc.exists: 
                    return child_by_desc
                time.sleep(0.5)

        if child_by_text.exists: 
            return child_by_text
        if child_by_desc.exists: 
            return child_by_desc
        
        return child_by_text
    
    
    def swipe_widget_to_center(self, widget, duration: float = 0.5) -> bool:
        """
        Swipes the screen to move a visible Widget to the center of the display.
        """
        if not widget.exists:
            self.log("⚠️ Cannot center Widget because it is not present on the screen.")
            return False

        try:
            screen_info = self.d.info
            screen_center_x = screen_info['displayWidth'] // 2
            screen_center_y = screen_info['displayHeight'] // 2

            widget_center_x, widget_center_y = widget.center()

            self.d.swipe(
                widget_center_x, 
                widget_center_y, 
                screen_center_x, 
                screen_center_y, 
                duration=duration
            )
            
            self.smart_sleep(1)
            return True
            
        except Exception as e:
            self.log(f"❌ Error while swiping Widget to center: {e}")
            return False
        
    def _get_screen_signature(self) -> int:
        """
        Generates a unique 'signature' of the current screen content to detect scroll changes.
        Filters out SystemUI elements to avoid timestamp or battery interference.
        """
        try:
            xml_dump = self.d.dump_hierarchy()
            root = ET.fromstring(xml_dump)
            texts = []
            
            for node in root.iter():
                pkg = node.attrib.get('package', '')
                
                if 'systemui' not in pkg.lower():
                    text = node.attrib.get('text', '')
                    desc = node.attrib.get('content-desc', '')
                    if text or desc:
                        texts.append(f"{text}|{desc}")
                        
            return hash("".join(texts))
        except Exception as e:
            self.log(f"⚠️ Error generating screen signature: {e}")
            return 0

    def is_at_bottom(self, check_scale: float = 0.3) -> bool:
        """
        Checks if the screen has been scrolled to the absolute bottom.
        """
        self.log("Checking if at the bottom of the page...")
        sig1 = self._get_screen_signature()
        
        self.swipe_up(scale=check_scale)
        
        sig2 = self._get_screen_signature()
        
        if sig1 == sig2:
            self.log("✔️ Reached page bottom.")
            return True
        else:
            self.log("🔄 More content available. Returning to previous position...")
            self.swipe_down(scale=check_scale)
            return False

    def is_at_top(self, check_scale: float = 0.3) -> bool:
        """
        Checks if the screen is currently at the absolute top.
        """
        self.log("Checking if at the top of the page...")
        sig1 = self._get_screen_signature()
        
        self.swipe_down(scale=check_scale)
        
        sig2 = self._get_screen_signature()
        
        if sig1 == sig2:
            self.log("✔️ Already at page top.")
            return True
        else:
            self.log("🔄 Not at top yet. Returning to previous position...")
            self.swipe_up(scale=check_scale)
            return False
    
    def scroll_to_bottom(self, max_swipes: int = 20, scale: float = 0.6) -> bool:
        """
        Continuously scrolls until the bottom of the page is detected or max_swipes is reached.
        """
        self.log("⏬ Scrolling to the bottom of the page...")
        
        for i in range(max_swipes):
            sig1 = self._get_screen_signature()
            
            self.swipe_up(scale=scale)
            self.smart_sleep(2) 
            
            sig2 = self._get_screen_signature()
            
            if sig1 == sig2:
                self.log(f"✔️ Reached bottom after {i + 1} swipes.")
                return True
                
        self.log(f"⚠️ Swiped {max_swipes} times; page might be too long or infinite.")
        return False

    def scroll_to_top(self, max_swipes: int = 20, scale: float = 0.6) -> bool:
        """
        Continuously scrolls until the top of the page is detected or max_swipes is reached.
        """
        self.log("⏫ Scrolling to the top of the page...")
        
        for i in range(max_swipes):
            sig1 = self._get_screen_signature()
            
            self.swipe_down(scale=scale)
            self.smart_sleep(1) 
            
            sig2 = self._get_screen_signature()
            
            if sig1 == sig2:
                self.log(f"✔️ Reached top after {i + 1} swipes.")
                return True
                
        self.log(f"⚠️ Swiped {max_swipes} times; may not have reached the absolute top.")
        return False