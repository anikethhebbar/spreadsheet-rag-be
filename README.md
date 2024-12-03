The frontend will start on `http://localhost:3000`

## Using the Application

1. Open your browser and go to `http://localhost:3000`
2. Upload your data file through the interface
3. Enter your query in the input field
4. The system will process your query using RAG and return relevant responses

## API Endpoints

- `POST /api/upload` - Upload data file
- `POST /api/query` - Process queries against the uploaded data

## Technologies Used

- **Backend**
  - Flask
  - Google Gemini API
  - Python RAG implementation

- **Frontend**
  - Next.js 13+
  - TailwindCSS
  - TypeScript

## Development

- Backend code is in the `app` directory
- Frontend code is in the `rag-frontend` directory
- API routes are defined in `app/routes/`

## Important Notes

- Make sure both backend and frontend servers are running simultaneously
- Keep your Gemini API key secure and never commit it to version control
- Large files should be processed in chunks to avoid memory issues
