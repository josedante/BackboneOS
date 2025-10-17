#!/bin/bash
# Monitor Django logs for page view event processing

echo "======================================================================"
echo "                    PAGE VIEW EVENT LOG MONITOR                       "
echo "======================================================================"
echo ""
echo "Monitoring Docker logs for page view event processing..."
echo "Press Ctrl+C to stop"
echo ""
echo "----------------------------------------------------------------------"

# Monitor backend container logs and filter for relevant entries
docker-compose logs -f backend | grep -E "(page_view|Page view|WebInteraction|Touchpoint|Channel|Medium|TouchpointType|Created|interaction|CRITICAL|ERROR|WARNING)" --line-buffered --color=always

