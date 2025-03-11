from utils.yaml_control import YamlHandler
from models.config_model import Config
from config import CONFIG_FILE


_data = YamlHandler(CONFIG_FILE).get_yaml_data()
config = Config(**_data)

if __name__ == '__main__':
    print(config)