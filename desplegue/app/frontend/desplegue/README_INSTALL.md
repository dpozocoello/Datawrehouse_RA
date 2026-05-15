# Dashboard ECO-SIEAA v1.01 - Paquete de Despliegue

Este paquete contiene todo lo necesario para instalar el Dashboard en servidores Linux.

## Estructura
- /app: CÃ³digo fuente y GeoJSON.
- /scripts: Instaladores para Rocky Linux y Ubuntu.
- /sql: Scripts de inicializaciÃ³n de Base de Datos.

## InstalaciÃ³n

1. Copiar esta carpeta al servidor (ej. /opt/dashboard).
2. Ejecutar el script correspondiente a su distribuciÃ³n:
   - Rocky Linux 10: ash scripts/install_rocky.sh
   - Ubuntu Server: ash scripts/install_ubuntu.sh
3. Configurar la base de datos PostgreSQL utilizando los scripts en /sql.
4. Ejecutar el dashboard: ./start_dashboard.sh

## Nota sobre PostgreSQL
AsegÃºrese de que el servidor tenga acceso a una base de datos PostgreSQL y que las credenciales en pp/Dash_board_RG_v1.01.py o variables de entorno sean correctas.
