while true;
do
    echo "restarting bash script"
    sleep 5s;
    python spreadsheet.py && break;
done
