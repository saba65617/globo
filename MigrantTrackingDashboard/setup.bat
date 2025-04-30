@echo off
echo Installing required packages...
"C:\Users\Saba Ali\AppData\Local\Programs\Python\Python313\python.exe" -m pip install --upgrade pip
"C:\Users\Saba Ali\AppData\Local\Programs\Python\Python313\python.exe" -m pip install plotly --no-cache-dir
"C:\Users\Saba Ali\AppData\Local\Programs\Python\Python313\python.exe" -m pip install pandas numpy streamlit folium streamlit-folium supabase python-dotenv
"C:\Users\Saba Ali\AppData\Local\Programs\Python\Python313\python.exe" -m pip install psycopg2-binary sqlalchemy
echo Installation complete!
pause 