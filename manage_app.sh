#!/bin/bash
# Management script for Streamlit Document Processing App

case $1 in
    start)
        sudo systemctl start streamlit-doc-processor.service
        echo "App started"
        ;;
    stop)
        sudo systemctl stop streamlit-doc-processor.service
        echo "App stopped"
        ;;
    restart)
        sudo systemctl restart streamlit-doc-processor.service
        echo "App restarted"
        ;;
    status)
        sudo systemctl status streamlit-doc-processor.service
        ;;
    logs)
        sudo journalctl -u streamlit-doc-processor.service -f
        ;;
    enable)
        sudo systemctl enable streamlit-doc-processor.service
        echo "App enabled for auto-start"
        ;;
    disable)
        sudo systemctl disable streamlit-doc-processor.service
        echo "App disabled from auto-start"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
