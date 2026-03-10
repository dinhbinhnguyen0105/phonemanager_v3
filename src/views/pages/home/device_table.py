# src/views/pages/home/device_table.py
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import Signal
from src.entities import Device
from src.constants import DeviceStatus

from src.models.table_model import DeviceTableModel
from src.database.connection import DatabaseManager


class DeviceTable(QTableView):
    devices_selected = Signal(list) 
    row_double_clicked = Signal(Device)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DeviceTableModel(DatabaseManager())
        self.setModel(self._model)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.ExtendedSelection)
        self.setEditTriggers(QTableView.NoEditTriggers)

        self._hide_columns(["uuid", "created_at", "updated_at"])
        self.doubleClicked.connect(self._on_row_double_clicked)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def _hide_columns(self, column_names: list[str]):
        record = self._model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setColumnHidden(i, field_name in column_names)

    def _parse_device_from_record(self, record) -> Device:
        status_str = record.value("device_status")
        try:
            status_enum = DeviceStatus(status_str)
        except ValueError:
            status_enum = DeviceStatus.OFFLINE
            
        return Device(
            uuid=record.value("uuid"),
            device_id=record.value("device_id"),
            device_name=record.value("device_name"),
            device_status=status_enum,
            device_root=bool(record.value("device_root")),
            created_at=record.value("created_at"),
            updated_at=record.value("updated_at")
        )

    def _on_selection_changed(self, selected, deselected):
        selected_devices = []
        for index in self.selectionModel().selectedRows():
            if index.isValid():
                record = self._model.record(index.row())
                device = self._parse_device_from_record(record)
                selected_devices.append(device)
        self.devices_selected.emit(selected_devices)

    def _on_row_double_clicked(self, index):
        if not index.isValid():
            return
        record = self._model.record(index.row())
        selected_device = self._parse_device_from_record(record)
        self.row_double_clicked.emit(selected_device)

    def on_device_state_changed(self, device: Device):
        self._model.select()