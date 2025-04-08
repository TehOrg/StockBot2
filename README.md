# TehStockbot2
Command for my friends to annoy each other with

Example Docker-compose:
```
    stockbot2:
        container_name: stockbot2
        image: ghcr.io/tehorg/stockbot2:main
        restart: unless-stopped
        env_file: ./stockbot2/stockbot2.env
```
Example env file:
```
DISCORD_TOKEN=\<Discord token\>
STOCKS_CHANNEL_ID=\<channel id\>
LOG_LEVEL=\<DEBUG | INFO | ERROR\> # This is optional
```
