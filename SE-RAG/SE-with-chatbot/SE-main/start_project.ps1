# Start the Python Backend
Write-Host "Starting Python Backend..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "chatbot_backend/app.py" -WorkingDirectory "G:\Code\SE 2\SE-RAG\SE-with-chatbot\SE-main"

# Start the Flutter Web App
Write-Host "Starting Flutter App..." -ForegroundColor Cyan
flutter run -d chrome

Write-Host "Project is running. Press Ctrl+C to stop." -ForegroundColor Yellow
