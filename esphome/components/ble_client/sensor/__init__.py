import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, ble_client, esp32_ble_tracker
from esphome.const import (
    DEVICE_CLASS_EMPTY,
    CONF_ID,
    STATE_CLASS_EMPTY,
    UNIT_EMPTY,
    ICON_EMPTY,
    CONF_TRIGGER_ID,
    CONF_SERVICE_UUID,
)
from esphome import automation
from .. import ble_client_ns

DEPENDENCIES = ["ble_client"]

CONF_CHARACTERISTIC_UUID = "characteristic_uuid"
CONF_DESCRIPTOR_UUID = "descriptor_uuid"

CONF_NOTIFY = "notify"
CONF_ON_NOTIFY = "on_notify"

BLESensor = ble_client_ns.class_(
    "BLESensor", sensor.Sensor, cg.PollingComponent, ble_client.BLEClientNode
)
BLESensorNotifyTrigger = ble_client_ns.class_(
    "BLESensorNotifyTrigger", automation.Trigger.template(cg.float_)
)

CONFIG_SCHEMA = cv.All(
    sensor.sensor_schema(
        UNIT_EMPTY, ICON_EMPTY, 0, DEVICE_CLASS_EMPTY, STATE_CLASS_EMPTY
    )
    .extend(
        {
            cv.GenerateID(): cv.declare_id(BLESensor),
            cv.Required(CONF_SERVICE_UUID): esp32_ble_tracker.bt_uuid,
            cv.Required(CONF_CHARACTERISTIC_UUID): esp32_ble_tracker.bt_uuid,
            cv.Optional(CONF_DESCRIPTOR_UUID): esp32_ble_tracker.bt_uuid,
            cv.Optional(CONF_NOTIFY, default=False): cv.boolean,
            cv.Optional(CONF_ON_NOTIFY): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        BLESensorNotifyTrigger
                    ),
                }
            ),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(ble_client.BLE_CLIENT_SCHEMA)
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    if len(config[CONF_SERVICE_UUID]) == len(esp32_ble_tracker.bt_uuid16_format):
        cg.add(
            var.set_service_uuid16(esp32_ble_tracker.as_hex(config[CONF_SERVICE_UUID]))
        )
    elif len(config[CONF_SERVICE_UUID]) == len(esp32_ble_tracker.bt_uuid32_format):
        cg.add(
            var.set_service_uuid32(esp32_ble_tracker.as_hex(config[CONF_SERVICE_UUID]))
        )
    elif len(config[CONF_SERVICE_UUID]) == len(esp32_ble_tracker.bt_uuid128_format):
        uuid128 = esp32_ble_tracker.as_hex_array(config[CONF_SERVICE_UUID])
        cg.add(var.set_service_uuid128(uuid128))

    if len(config[CONF_CHARACTERISTIC_UUID]) == len(esp32_ble_tracker.bt_uuid16_format):
        cg.add(
            var.set_char_uuid16(
                esp32_ble_tracker.as_hex(config[CONF_CHARACTERISTIC_UUID])
            )
        )
    elif len(config[CONF_CHARACTERISTIC_UUID]) == len(
        esp32_ble_tracker.bt_uuid32_format
    ):
        cg.add(
            var.set_char_uuid32(
                esp32_ble_tracker.as_hex(config[CONF_CHARACTERISTIC_UUID])
            )
        )
    elif len(config[CONF_CHARACTERISTIC_UUID]) == len(
        esp32_ble_tracker.bt_uuid128_format
    ):
        uuid128 = esp32_ble_tracker.as_hex_array(config[CONF_CHARACTERISTIC_UUID])
        cg.add(var.set_char_uuid128(uuid128))

    if CONF_DESCRIPTOR_UUID in config:
        if len(config[CONF_DESCRIPTOR_UUID]) == len(esp32_ble_tracker.bt_uuid16_format):
            cg.add(
                var.set_descr_uuid16(
                    esp32_ble_tracker.as_hex(config[CONF_DESCRIPTOR_UUID])
                )
            )
        elif len(config[CONF_DESCRIPTOR_UUID]) == len(
            esp32_ble_tracker.bt_uuid32_format
        ):
            cg.add(
                var.set_descr_uuid32(
                    esp32_ble_tracker.as_hex(config[CONF_DESCRIPTOR_UUID])
                )
            )
        elif len(config[CONF_DESCRIPTOR_UUID]) == len(
            esp32_ble_tracker.bt_uuid128_format
        ):
            uuid128 = esp32_ble_tracker.as_hex_array(config[CONF_DESCRIPTOR_UUID])
            cg.add(var.set_descr_uuid128(uuid128))

    yield cg.register_component(var, config)
    yield ble_client.register_ble_node(var, config)
    cg.add(var.set_enable_notify(config[CONF_NOTIFY]))
    yield sensor.register_sensor(var, config)
    for conf in config.get(CONF_ON_NOTIFY, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        yield ble_client.register_ble_node(trigger, config)
        yield automation.build_automation(trigger, [(float, "x")], conf)
