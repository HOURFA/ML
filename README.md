## 修改檔案
  必須修改mlgame中__main__.py，才可以通過GUI讀取到遊戲的配置文件。
  
  將
  ```bash
    # 1. parse command line
    arg_obj = parse_cmd_and_get_arg_obj(sys.argv[1:])

    # 2. get parsed_game_params
    from mlgame.argument.game_argument import GameConfig
    game_config = GameConfig(arg_obj.game_folder.__str__())
  ```
修改成
  ```bash
   # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run MLGame with specific configuration.")
    parser.add_argument("--config", type=str, required=False, help="Path to the game configuration file.")
    args, unknown = parser.parse_known_args()
    
    # Load game configuration
    config_path = args.config
    # Parse other MLGame arguments
    arg_obj = parse_cmd_and_get_arg_obj(unknown)
    
    # Get parsed game params
    from mlgame.argument.game_argument import GameConfig    
    if config_path is not None:
        game_config = GameConfig(config_path)
    else:
        game_config = GameConfig(arg_obj.game_folder.__str__())
```
    
