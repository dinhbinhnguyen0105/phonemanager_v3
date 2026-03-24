import re
import sys
import traceback
from random import randint
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from src.entities import Job
from src.automation.core.base_automator import BaseAutomator
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager
    from PySide6.QtCore import SignalInstance

def run_list_marketplace_share(device_id: str, job: Job, logger_signal: "SignalInstance", controllers: Optional["ControllerManager"] = None):
    """
    Main execution flow for listing a property on Facebook Marketplace.
    
    This function handles the entire lifecycle of a Marketplace listing task:
    1. Media deployment (pushing images to device).
    2. Navigation to the Real Estate listing form.
    3. Filling out listing details (Title, Price, Category, etc.).
    4. Selecting high-member groups for cross-posting.
    5. Cleanup and teardown.
    """
    bot = BaseAutomator(device_id, logger_signal)
    if controllers:
        user_info = controllers.user_controller.get_by_id(job.user_uuid)
        user_id = user_info.user_id if user_info else 0
    else:
        user_id = 0 
    
    try:
        image_paths = job.parameters.get("image_paths")
        if image_paths:
            bot.push_media(image_paths, user_id)


        # Navigation loop with retries
        form_opened = False
        for i in range(3):
            if _goto_home_for_sell(bot):
                form_opened = True
                break
            logger.debug(f"Navigation attempt failed: {i+1}")
            bot.smart_sleep(3)
        
        if not form_opened:
            raise Exception("Failed to open listing form after multiple attempts")

        # return
        # Form filling sequence
        _fill_photos(bot, len(image_paths if image_paths else []))
        _fill_listing_details(bot, job.parameters)
        _click_next_button(bot)
        _list_more_place(bot)
        _click_publish_button(bot)
        bot.smart_sleep(10)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
        full_traceback = "".join(tb_details)
        
        last_frame = traceback.extract_tb(exc_traceback)[-1]
        file_name = last_frame.filename
        line_number = last_frame.lineno
        error_name = exc_type.__name__ if exc_type else "Unknown"

        logger.error(f"Full Traceback for {device_id}:\n{full_traceback}")
        raise e
    finally:
        bot.cleanup_media()
        bot.d.app_stop("com.facebook.katana")
        bot.teardown()

def _goto_home_for_sell(bot: BaseAutomator) -> bool:
    """
    Navigates the Facebook UI to reach the 'Home for Sale or Rent' listing form.
    
    Uses a retry mechanism to handle transient UI glitches or app loading issues.
    """
    for attempt in range(3):
        try:
            bot.log(f"🔄 Opening Marketplace (Attempt {attempt + 1}/3)...")
            bot.launch_app("com.facebook.katana", "fb://marketplace")
            
            sell_btn = bot.get_button_by_text("sell", timeout=15)
            if not sell_btn.exists:
                raise Exception("Could not find 'Sell' button")
            sell_btn.click_exists(timeout=5)
            bot.smart_sleep(1) 
            
            bot.log("Checking for 'Create listing' button...")
            create_btn = bot.get_button_by_text("create", timeout=3)
            
            if create_btn.exists:
                if not bot.click_button_with_retry("create", max_retries=3, timeout=3, wait_gone_timeout=5):
                    raise Exception("App stuck, no response after clicking 'Create'")
            else:
                bot.log("⏩ 'Create' button not found, skipping step.")
            
            if bot.click_button_with_retry("sale or rent", max_retries=3, timeout=10, wait_gone_timeout=5):
                bot.log("✔️ Navigated to listing form successfully!")
                return True
            else:
                raise Exception("Could not click 'Sale or rent' or page did not transition")

        except Exception as e:
            bot.log(f"⚠️ Error in cycle {attempt + 1}: {e}")
            continue 
            
    bot.log("❌ Failed to open form after 3 attempts.")
    return False

def _fill_photos(bot: BaseAutomator, photo_num: int = 1):
    """
    Selects photos from the Android Gallery.
    
    Prioritizes recent photos by iterating through the grid in reverse order.
    """
    if not bot.click_button_with_retry("add photos", timeout=15):
        raise Exception("Could not click 'Add photos' button")
    
    bot.smart_sleep(2) 
    
    grid_view = bot.get_elements_by_widget("android.widget.GridView")
    if not grid_view.exists:
        raise Exception("Could not locate the Photo Gallery GridView")
    
    photo_widgets = bot.get_interactable_from_parent(
        grid_view[0], 
        "android.view.ViewGroup", 
        text="photo", 
        timeout=30
    )
    
    count = photo_widgets.count
    if count == 0:
        raise Exception("No items labeled 'photo' found in gallery")
        
    actual_num = min(count, photo_num)
    
    for i in reversed(range(actual_num)):
        photo_widgets[i].click_exists(timeout=10)
        bot.smart_sleep(1)
    
    if not bot.click_button_with_retry("next", timeout=15):
        raise Exception("Could not click 'Next' button")

def _fill_listing_details(bot: BaseAutomator, payload: Dict[str, Any]):
    """
    Orchestrates the input of listing details (Title, Price, Category, Location, Description).
    """
    _set_title(bot, payload.get("title", ""))
    _set_price(bot)
    _set_category(bot)
    _set_location(bot, "Da Lat")
    _set_description(bot, payload.get("description", ""))

def _set_title(bot: BaseAutomator, title: str):
    """
    Enters the property title in uppercase.
    """
    title_group = bot.get_widget_by_text("android.view.ViewGroup", "title", timeout=30)
    if not title_group.exists:
        raise Exception("Could not find 'Title' field container")
    
    bot.swipe_widget_to_center(title_group)
    title_group.click()
    title_input = bot.get_interactable_from_parent(title_group, "android.widget.EditText", timeout=30)
    
    if not title_input.exists:
        raise Exception("Could not find EditText within Title container")
        
    title_input.send_keys(title.upper())

def _set_price(bot: BaseAutomator):
    """
    Enters a randomized price.
    """
    price_group = bot.get_widget_by_text("android.view.ViewGroup", "price", timeout=30)
    if not price_group.exists:
        raise Exception("Could not find 'Price' field container")
    
    bot.swipe_widget_to_center(price_group)
    price_group.click()
    price_input = bot.get_interactable_from_parent(price_group, "android.widget.EditText", timeout=30)
    
    if not price_input.exists:
        raise Exception("Could not find EditText within Price container")
        
    price_input.send_keys(str(randint(1, 1000)))

def _set_category(bot: BaseAutomator):
    """
    Selects the 'Home(s) for sale' category.
    """
    category_btn = bot.get_button_by_text("category", timeout=30)
    if not category_btn.exists:
        raise Exception("Could not find 'Category' button")
    bot.swipe_widget_to_center(category_btn)
    category_btn.click()

    sale_option = bot.get_button_by_text("sale", timeout=30)
    if not sale_option.exists:
        raise Exception("Could not find 'Home(s) for sale' option")
    sale_option.click()

def _set_location(bot: BaseAutomator, city_name: str):
    """
    Updates the listing location.
    """
    location_btn = bot.get_button_by_text("location", timeout=30)
    if not location_btn.exists:
        raise Exception("Could not find 'Location' entry point")
    bot.swipe_widget_to_center(location_btn)
    location_btn.click()

    search_input = bot.get_widget_by_text("android.widget.EditText", "Search", timeout=30)
    if not search_input.exists:
        raise Exception("Could not find 'Search' field container in location picker")
    
    search_input.click()
    search_input.send_keys(city_name)

    city_suggestion = bot.get_button_by_text(city_name, timeout=30)
    if not city_suggestion.exists:
        raise Exception(f"Could not find suggestion for '{city_name}'")
    city_suggestion.click()

    apply_btn = bot.get_button_by_text("apply", timeout=30)
    if not apply_btn.exists:
        raise Exception("Could not find 'Apply' button")
    apply_btn.click()

def _set_description(bot: BaseAutomator, description: str):
    """
    Inputs the property description.
    """
    description_group = bot.get_widget_by_text("android.view.ViewGroup", "description", timeout=30)
    if not description_group.exists:
        raise Exception("Could not find 'Description' field container")
    
    bot.swipe_widget_to_center(description_group)
    description_group.click()
    description_input = bot.get_interactable_from_parent(description_group, "android.widget.EditText", timeout=30)
    description_input.send_keys(description)

def _click_next_button(bot: BaseAutomator):
    """
    Clicks the 'Next' button to proceed to the cross-posting selection.
    """
    next_button = bot.get_button_by_text("next", timeout=30)
    if not next_button.exists:
        raise Exception("Could not find 'Next' button")
    next_button.click()

def _list_more_place(bot: BaseAutomator):
    """
    Intelligent cross-posting logic:
    1. Swipes down to gather all visible group data from checkboxes.
    2. Filters for the Top 20 groups based on member count.
    3. Swipes back up and clicks the checkboxes for the identified Top 20 groups.
    """
    collected_groups = {} 
    max_swipes = 10
    
    # PHASE 1: Data Collection & Scroll Down
    for _ in range(max_swipes):
        checkboxes = bot.get_elements_by_widget("android.widget.CheckBox", timeout=2)
        
        for box in checkboxes:
            try:
                desc = box.info.get('contentDescription', '')
                if desc and desc not in collected_groups:
                    members = _parse_member_count(desc)
                    collected_groups[desc] = members
            except:
                pass 
        
        sig1 = bot._get_screen_signature()
        bot.swipe_up(scale=1)
        sig2 = bot._get_screen_signature()
        
        if sig1 == sig2:
            break

    # PHASE 2: Sorting and Filtering Top 20
    sorted_groups = sorted(collected_groups.items(), key=lambda item: item[1], reverse=True)
    top_20_groups = dict(sorted_groups[:20])
    target_descs = set(top_20_groups.keys()) 
    
    # PHASE 3: Scroll Up & Click Target Groups
    clicked_groups = set() 
    
    for _ in range(max_swipes):
        checkboxes = bot.get_elements_by_widget("android.widget.CheckBox", timeout=2)
        
        for box in checkboxes:
            try:
                desc = box.info.get('contentDescription', '')
                if desc in target_descs and desc not in clicked_groups:
                    box.click_exists(timeout=2)
                    clicked_groups.add(desc)
            except:
                pass

        if len(clicked_groups) >= len(target_descs):
            break
            
        sig1 = bot._get_screen_signature()
        bot.swipe_down(scale=1)
        sig2 = bot._get_screen_signature()
        
        if sig1 == sig2:
            break

def _click_publish_button(bot: BaseAutomator):
    """
    Clicks the 'Publish' button to finalize the listing or proceed to cross-posting.
    
    This method implements a two-tier strategy for high reliability:
    1. Primary: Targets the specific Facebook 'resourceId' (mp_composer_post), 
       which is the most stable identifier for this action.
    2. Fallback: Reverts to a text-based search if the resource ID is not found 
       (e.g., due to a UI update).

    Args:
        bot (BaseAutomator): The automation controller instance.

    Returns:
        bool: True if the button was clicked and successfully disappeared from the UI.

    Raises:
        Exception: If the button is clicked but the app hangs, or if the button 
                  cannot be found using either the ID or text fallback.
    """
    bot.log("Locating and clicking the 'Publish' button...")
    
    publish_btn = bot.d(resourceId="mp_composer_post")
    
    if publish_btn.exists(timeout=10):
        publish_btn.click_exists(timeout=5)
        is_published = publish_btn.wait_gone(timeout=15)
        
        if is_published:
            bot.log("✔️ 'Publish' button clicked successfully!")
            return True
        else:
            raise Exception("Clicked 'Publish' but the application failed to respond or load.")
            
    else:
        bot.log("⚠️ Resource ID 'mp_composer_post' not found, attempting text-based search...")
        is_published = bot.click_button_with_retry("publish", timeout=10)
        
        if not is_published:
            raise Exception("Could not find or interact with the 'Publish' button using ID or text.")
            
        return is_published


def _parse_member_count(desc: str) -> int:
    """
    Helper function: Parses member count from content-description strings.
    Example: "Private group • 81.3K members" -> 81300
    """
    if not desc:
        return 0
    match = re.search(r'([\d\.]+)([KMkm]?)\s*(?:members|thành viên)', desc, re.IGNORECASE)
    if not match:
        return 0
        
    num_str, multiplier = match.groups()
    try:
        num = float(num_str)
        if multiplier.upper() == 'K':
            num *= 1000
        elif multiplier.upper() == 'M':
            num *= 1000000
        return int(num)
    except:
        return 0
    