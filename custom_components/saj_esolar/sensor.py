"""Alternative for the esolar local API sensor. Unfortunally there is no public api.

This Sensor will read the private api of the eSolar portal at https://inversores-style.greenheiss.com
"""

from collections.abc import Callable
from datetime import date, datetime, timedelta
import logging
from typing import Any, Final

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, H1_SENSORS, SAJ_SENSORS, SENSOR_TYPES
from .coordinator import EsolarDataUpdateCoordinator

CONF_PLANT_ID: Final = "plant_id"

_LOGGER = logging.getLogger(__name__)

DEVICE_TYPES = {
    "Inverter": 0,
    "Meter": 1,  # TODO: Pending to confirm
    "Battery": 2,
    0: "Inverter",
    1: "Meter",  # TODO: Pending to confirm
    2: "Battery",
}

SENSOR_PREFIX = "esolar "  # do not change.
ATTR_MEASUREMENT = "measurement"
ATTR_SECTION = "section"


def _toPercentage(value: str) -> str:
    return float(value.strip("%"))


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
):
    """Set up the eSolar sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    config = entry.data
    entities = []
    if config[CONF_SENSORS] == "h1":
        sensorlist = H1_SENSORS
    else:
        sensorlist = SAJ_SENSORS

    for description in SENSOR_TYPES:
        _LOGGER.debug("Setting up esolar sensor: %s", description.key)
        if description.key in sensorlist:
            sensor = SAJeSolarMeterSensor(
                coordinator,
                description,
                config.get(CONF_SENSORS),
                config.get(CONF_PLANT_ID),
            )
            entities.append(sensor)
    async_add_entities(entities, True)
    return True


class SAJeSolarMeterSensor(CoordinatorEntity, SensorEntity):
    """Collecting data and return sensor entity."""

    def __init__(
        self,
        coordinator: EsolarDataUpdateCoordinator,
        description: SensorEntityDescription,
        sensors: str,
        plant_id: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        _LOGGER.debug("Initializing esolar sensor: %s", description.key)
        self.entity_description = description
        self._state = None
        self.sensors = sensors
        self.plant_id = plant_id
        self._type = self.entity_description.key
        self._attr_icon = self.entity_description.icon
        self._attr_name = f"{SENSOR_PREFIX}{self.entity_description.name}"
        self._attr_state_class = self.entity_description.state_class
        self._attr_native_unit_of_measurement = (
            self.entity_description.native_unit_of_measurement
        )
        self._attr_device_class = self.entity_description.device_class
        self._attr_unique_id = f"{SENSOR_PREFIX}_{self._type}"

        self._discovery = False
        self._dev_id = {}

    @property
    def native_value(self) -> StateType | date | datetime:
        """Handle updated data from the coordinator."""
        energy = self.coordinator.data
        if energy:
            if self._type == "devOnlineNum":
                if "devOnlineNum" in energy["plantDetail"]:
                    if energy["plantDetail"]["devOnlineNum"] is not None:
                        self._state = (
                            True
                            if int(energy["plantDetail"]["devOnlineNum"])
                            else False
                        )
            if self._type == "nowPower":
                if "nowPower" in energy["plantDetail"]:
                    if energy["plantDetail"]["nowPower"] is not None:
                        self._state = float(energy["plantDetail"]["nowPower"])
            if self._type == "runningState":
                if "runningState" in energy["plantDetail"]:
                    if energy["plantDetail"]["runningState"] is not None:
                        self._state = (
                            True
                            if int(energy["plantDetail"]["runningState"])
                            else False
                        )
            if self._type == "todayElectricity":
                if "todayElectricity" in energy["plantDetail"]:
                    if energy["plantDetail"]["todayElectricity"] is not None:
                        self._state = float(energy["plantDetail"]["todayElectricity"])
            if self._type == "monthElectricity":
                if "monthElectricity" in energy["plantDetail"]:
                    if energy["plantDetail"]["monthElectricity"] is not None:
                        self._state = float(energy["plantDetail"]["monthElectricity"])
            if self._type == "yearElectricity":
                if "yearElectricity" in energy["plantDetail"]:
                    if energy["plantDetail"]["yearElectricity"] is not None:
                        self._state = float(energy["plantDetail"]["yearElectricity"])
            if self._type == "totalElectricity":
                if "totalElectricity" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalElectricity"] is not None:
                        self._state = float(energy["plantDetail"]["totalElectricity"])
            if self._type == "todayGridIncome":
                if "todayGridIncome" in energy["plantDetail"]:
                    if energy["plantDetail"]["todayGridIncome"] is not None:
                        self._state = float(energy["plantDetail"]["todayGridIncome"])
            if self._type == "income":
                if "income" in energy["plantDetail"]:
                    if energy["plantDetail"]["income"] is not None:
                        self._state = float(energy["plantDetail"]["income"])
            if self._type == "selfUseRate":
                if "selfUseRate" in energy["plantDetail"]:
                    selfUseRate = energy["plantDetail"]["selfUseRate"]
                    if selfUseRate is not None:
                        self._state = _toPercentage((selfUseRate))
            if self._type == "totalBuyElec":
                if "totalBuyElec" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalBuyElec"] is not None:
                        self._state = float(energy["plantDetail"]["totalBuyElec"])
            if self._type == "totalConsumpElec":
                if "totalConsumpElec" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalConsumpElec"] is not None:
                        self._state = float(energy["plantDetail"]["totalConsumpElec"])
            if self._type == "totalSellElec":
                if "totalSellElec" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalSellElec"] is not None:
                        self._state = float(energy["plantDetail"]["totalSellElec"])
            if self._type == "lastUploadTime":
                if "lastUploadTime" in energy["plantDetail"]:
                    if energy["plantDetail"]["lastUploadTime"] is not None:
                        self._state = energy["plantDetail"]["lastUploadTime"]
            if self._type == "totalPlantTreeNum":
                if "totalPlantTreeNum" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalPlantTreeNum"] is not None:
                        self._state = energy["plantDetail"]["totalPlantTreeNum"]
            if self._type == "totalReduceCo2":
                if "totalReduceCo2" in energy["plantDetail"]:
                    if energy["plantDetail"]["totalReduceCo2"] is not None:
                        self._state = energy["plantDetail"]["totalReduceCo2"]
            if self._type == "currency":
                if "currency" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["currency"] is not None:
                        self._state = energy["plantList"][self.plant_id]["currency"]
            if self._type == "plantuid":
                if "plantuid" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["plantuid"] is not None:
                        self._state = energy["plantList"][self.plant_id]["plantuid"]
            if self._type == "plantname":
                if "plantname" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["plantname"] is not None:
                        self._state = energy["plantList"][self.plant_id]["plantname"]
            if self._type == "isOnline":
                if "isOnline" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["isOnline"] is not None:
                        self._state = (
                            energy["plantList"][self.plant_id]["isOnline"].upper()
                            == "Y"  # boolean from Y/N
                        )
            if self._type == "address":
                if "address" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["address"] is not None:
                        self._state = energy["plantList"][self.plant_id]["address"]
            if self._type == "systemPower":
                if "systempower" in energy["plantList"][self.plant_id]:
                    if energy["plantList"][self.plant_id]["systempower"] is not None:
                        self._state = energy["plantList"][self.plant_id]["systempower"]

            if self._type == "peakPower":
                if "peakPower" in energy:
                    if energy["peakPower"] is not None:
                        self._state = float(energy["peakPower"])
            if self._type == "status":
                if "status" in energy:
                    if energy["status"] is not None:
                        self._state = energy["status"]

            ########################################################################## SAJ h1
            if self.sensors == "h1":
                if self._type == "chargeElec":
                    if "chargeElec" in energy["viewBean"]:
                        if energy["viewBean"]["chargeElec"] is not None:
                            self._state = float(energy["viewBean"]["chargeElec"])
                if self._type == "dischargeElec":
                    if "dischargeElec" in energy["viewBean"]:
                        if energy["viewBean"]["dischargeElec"] is not None:
                            self._state = float(energy["viewBean"]["dischargeElec"])
                if self._type == "buyElec":
                    if "pvElec" in energy["viewBean"]:
                        if energy["viewBean"]["buyElec"] is not None:
                            self._state = float(energy["viewBean"]["buyElec"])
                if self._type == "buyRate":
                    if "buyRate" in energy["viewBean"]:
                        if energy["viewBean"]["buyRate"] is not None:
                            self._state = _toPercentage(energy["viewBean"]["buyRate"])
                if self._type == "pvElec":
                    if "pvElec" in energy["viewBean"]:
                        if energy["viewBean"]["pvElec"] is not None:
                            self._state = float(energy["viewBean"]["pvElec"])
                if self._type == "selfConsumedEnergy1":
                    if "selfConsumedEnergy1" in energy["viewBean"]:
                        if energy["viewBean"]["selfConsumedEnergy1"] is not None:
                            self._state = float(
                                energy["viewBean"]["selfConsumedEnergy1"]
                            )
                if self._type == "selfConsumedEnergy2":
                    if "selfConsumedEnergy2" in energy["viewBean"]:
                        if energy["viewBean"]["selfConsumedEnergy2"] is not None:
                            self._state = float(
                                energy["viewBean"]["selfConsumedEnergy2"]
                            )
                if self._type == "selfConsumedRate1":
                    if "selfConsumedRate1" in energy["viewBean"]:
                        if energy["viewBean"]["selfConsumedRate1"] is not None:
                            self._state = _toPercentage(
                                energy["viewBean"]["selfConsumedRate1"]
                            )
                if self._type == "selfConsumedRate2":
                    if "selfConsumedRate2" in energy["viewBean"]:
                        if energy["viewBean"]["selfConsumedRate2"] is not None:
                            self._state = _toPercentage(
                                energy["viewBean"]["selfConsumedRate2"]
                            )
                if self._type == "sellElec":
                    if "sellElec" in energy["viewBean"]:
                        if energy["viewBean"]["sellElec"] is not None:
                            self._state = float(energy["viewBean"]["sellElec"])
                if self._type == "sellRate":
                    if "sellRate" in energy["viewBean"]:
                        if energy["viewBean"]["sellRate"] is not None:
                            self._state = _toPercentage(energy["viewBean"]["sellRate"])
                if self._type == "useElec":
                    if "useElec" in energy["viewBean"]:
                        if energy["viewBean"]["useElec"] is not None:
                            self._state = float(energy["viewBean"]["useElec"])
                # storeDevicePower
                if self._type == "batCapcity":
                    if "batCapcity" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["batCapcity"] is not None:
                            self._state = float(
                                energy["storeDevicePower"]["batCapcity"]
                            )
                if self._type == "isStorageAlarm":
                    if "isStorageAlarm" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["isStorageAlarm"] is not None:
                            self._state = int(
                                energy["storeDevicePower"]["isStorageAlarm"]
                            )
                if self._type == "batCurr":
                    if "batCurr" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["batCurr"] is not None:
                            self._state = float(energy["storeDevicePower"]["batCurr"])
                if self._type == "batEnergyPercent":
                    if "batEnergyPercent" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["batEnergyPercent"] is not None:
                            self._state = float(
                                energy["storeDevicePower"]["batEnergyPercent"]
                            )
                if self._type == "batteryDirection":
                    if "batteryDirection" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["batteryDirection"] is not None:
                            if energy["storeDevicePower"]["batteryDirection"] == 0:
                                self._state = "Standby"
                            elif energy["storeDevicePower"]["batteryDirection"] == 1:
                                self._state = "Discharging"
                            elif energy["storeDevicePower"]["batteryDirection"] == -1:
                                self._state = "Charging"
                            else:
                                self._state = f"Unknown: {energy['storeDevicePower']['batteryDirection']}"
                if self._type == "batteryPower":
                    if "batteryPower" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["batteryPower"] is not None:
                            self._state = float(
                                energy["storeDevicePower"]["batteryPower"]
                            )
                if self._type == "gridDirection":
                    if "gridDirection" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["gridDirection"] is not None:
                            if energy["storeDevicePower"]["gridDirection"] == 1:
                                self._state = "Exporting"
                            elif energy["storeDevicePower"]["gridDirection"] == -1:
                                self._state = "Importing"
                            else:
                                self._state = energy["storeDevicePower"][
                                    "gridDirection"
                                ]
                                _LOGGER.error(
                                    "Grid Direction unknown value: %s", self._state
                                )
                if self._type == "gridPower":
                    if "gridPower" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["gridPower"] is not None:
                            self._state = float(energy["storeDevicePower"]["gridPower"])
                if self._type == "h1Online":
                    if "isOnline" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["isOnline"] is not None:
                            self._state = (
                                True
                                if int(energy["storeDevicePower"]["isOnline"])
                                else False
                            )
                if self._type == "outPower":
                    if "outPower" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["outPower"] is not None:
                            self._state = float(energy["storeDevicePower"]["outPower"])
                if self._type == "outPutDirection":
                    if "outPutDirection" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["outPutDirection"] is not None:
                            if energy["storeDevicePower"]["outPutDirection"] == 1:
                                self._state = "Exporting"
                            elif energy["storeDevicePower"]["outPutDirection"] == -1:
                                self._state = "Importing"
                            else:
                                self._state = energy["storeDevicePower"][
                                    "outPutDirection"
                                ]
                                _LOGGER.error(
                                    "Value for outPut Direction unknown: %s",
                                    self._state,
                                )
                if self._type == "pvDirection":
                    if "pvDirection" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["pvDirection"] is not None:
                            if energy["storeDevicePower"]["pvDirection"] == 1:
                                self._state = "Exporting"
                            elif energy["storeDevicePower"]["pvDirection"] == -1:
                                self._state = "Importing"
                            else:
                                self._state = energy["storeDevicePower"]["pvDirection"]
                                _LOGGER.error(
                                    "Value for pv Direction unknown: %s", self._state
                                )
                if self._type == "pvPower":
                    if "pvPower" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["pvPower"] is not None:
                            self._state = float(energy["storeDevicePower"]["pvPower"])
                if self._type == "solarPower":
                    if "solarPower" in energy["storeDevicePower"]:
                        if energy["storeDevicePower"]["solarPower"] is not None:
                            self._state = float(
                                energy["storeDevicePower"]["solarPower"]
                            )
            ########################################################################## Sec module Sensors:
            if self.sensors == "saj_sec":
                # getPlantMeterChartData - viewBeam
                if self._type == "pvElec":
                    if "pvElec" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["pvElec"]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"]["pvElec"]
                            )
                if self._type == "useElec":
                    if "useElec" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["useElec"]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"]["useElec"]
                            )
                if self._type == "buyElec":
                    if "buyElec" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["buyElec"]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"]["buyElec"]
                            )
                if self._type == "sellElec":
                    if "sellElec" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["sellElec"]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"]["sellElec"]
                            )
                if self._type == "selfConsumedEnergy1":
                    if (
                        "selfConsumedEnergy1"
                        in energy["getPlantMeterChartData"]["viewBean"]
                    ):
                        if (
                            energy["getPlantMeterChartData"]["viewBean"][
                                "selfConsumedEnergy1"
                            ]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"][
                                    "selfConsumedEnergy1"
                                ]
                            )
                if self._type == "selfConsumedEnergy2":
                    if (
                        "selfConsumedEnergy2"
                        in energy["getPlantMeterChartData"]["viewBean"]
                    ):
                        if (
                            energy["getPlantMeterChartData"]["viewBean"][
                                "selfConsumedEnergy2"
                            ]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"][
                                    "selfConsumedEnergy2"
                                ]
                            )
                if self._type == "reduceCo2":
                    if "reduceCo2" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["reduceCo2"]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["viewBean"][
                                    "reduceCo2"
                                ]
                            )
                if self._type == "buyRate":
                    if "buyRate" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["buyRate"]
                            is not None
                        ):
                            self._state = _toPercentage(
                                energy["getPlantMeterChartData"]["viewBean"]["buyRate"]
                            )
                if self._type == "sellRate":
                    if "sellRate" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["sellRate"]
                            is not None
                        ):
                            self._state = _toPercentage(
                                energy["getPlantMeterChartData"]["viewBean"]["sellRate"]
                            )
                if self._type == "selfConsumedRate1":
                    if (
                        "selfConsumedRate1"
                        in energy["getPlantMeterChartData"]["viewBean"]
                    ):
                        if (
                            energy["getPlantMeterChartData"]["viewBean"][
                                "selfConsumedRate1"
                            ]
                            is not None
                        ):
                            self._state = _toPercentage(
                                energy["getPlantMeterChartData"]["viewBean"][
                                    "selfConsumedRate1"
                                ]
                            )
                if self._type == "selfConsumedRate2":
                    if (
                        "selfConsumedRate2"
                        in energy["getPlantMeterChartData"]["viewBean"]
                    ):
                        if (
                            energy["getPlantMeterChartData"]["viewBean"][
                                "selfConsumedRate2"
                            ]
                            is not None
                        ):
                            self._state = _toPercentage(
                                energy["getPlantMeterChartData"]["viewBean"][
                                    "selfConsumedRate2"
                                ]
                            )
                if self._type == "plantTreeNum":
                    if "plantTreeNum" in energy["getPlantMeterChartData"]["viewBean"]:
                        if (
                            energy["getPlantMeterChartData"]["viewBean"]["plantTreeNum"]
                            is not None
                        ):
                            self._state = energy["getPlantMeterChartData"]["viewBean"][
                                "plantTreeNum"
                            ]

                if self._type == "homeLoadPower":
                    if "dataCountList" in energy:
                        if (
                            energy["getPlantMeterChartData"]["dataCountList"][1][-1]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["dataCountList"][1][-1]
                            )
                if self._type == "solarLoadPower":
                    if "dataCountList" in energy:
                        if (
                            energy["getPlantMeterChartData"]["dataCountList"][2][-1]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["dataCountList"][2][-1]
                            )
                if self._type == "exportPower":
                    if "dataCountList" in energy:
                        if (
                            energy["getPlantMeterChartData"]["dataCountList"][3][-1]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["dataCountList"][3][-1]
                            )
                if self._type == "gridLoadPower":
                    if "dataCountList" in energy:
                        if (
                            energy["getPlantMeterChartData"]["dataCountList"][4][-1]
                            is not None
                        ):
                            self._state = float(
                                energy["getPlantMeterChartData"]["dataCountList"][4][-1]
                            )

                # getPlantMeterDetailInfo

                if self._type == "selfUseRate":
                    if (
                        "selfUseRate"
                        in energy["getPlantMeterDetailInfo"]["plantDetail"]
                    ):
                        selfUse = energy["getPlantMeterDetailInfo"]["plantDetail"][
                            "selfUseRate"
                        ]
                        if selfUse is not None:
                            self._state = _toPercentage(selfUse)
                if self._type == "totalPvEnergy":
                    if (
                        "totalPvEnergy"
                        in energy["getPlantMeterDetailInfo"]["plantDetail"]
                    ):
                        if (
                            energy["getPlantMeterDetailInfo"]["plantDetail"][
                                "totalPvEnergy"
                            ]
                            is not None
                        ):
                            self._state = energy["getPlantMeterDetailInfo"][
                                "plantDetail"
                            ]["totalPvEnergy"]
                if self._type == "totalLoadEnergy":
                    if (
                        "totalLoadEnergy"
                        in energy["getPlantMeterDetailInfo"]["plantDetail"]
                    ):
                        if (
                            energy["getPlantMeterDetailInfo"]["plantDetail"][
                                "totalLoadEnergy"
                            ]
                            is not None
                        ):
                            self._state = energy["getPlantMeterDetailInfo"][
                                "plantDetail"
                            ]["totalLoadEnergy"]
                if self._type == "totalBuyEnergy":
                    if (
                        "totalBuyEnergy"
                        in energy["getPlantMeterDetailInfo"]["plantDetail"]
                    ):
                        if (
                            energy["getPlantMeterDetailInfo"]["plantDetail"][
                                "totalBuyEnergy"
                            ]
                            is not None
                        ):
                            self._state = energy["getPlantMeterDetailInfo"][
                                "plantDetail"
                            ]["totalBuyEnergy"]
                if self._type == "totalSellEnergy":
                    if (
                        "totalSellEnergy"
                        in energy["getPlantMeterDetailInfo"]["plantDetail"]
                    ):
                        if (
                            energy["getPlantMeterDetailInfo"]["plantDetail"][
                                "totalSellEnergy"
                            ]
                            is not None
                        ):
                            self._state = energy["getPlantMeterDetailInfo"][
                                "plantDetail"
                            ]["totalSellEnergy"]

        # -Debug- adding sensor
        _LOGGER.debug("Device: %s , State %s", self._type, self._state)
        return self._state
