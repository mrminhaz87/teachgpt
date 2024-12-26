import { promises as fs } from 'fs';
import path from 'path';

export async function GET({ url }) {
  try {
    const requestPath = url.searchParams.get('path') || '';
    const dirPath = path.join('public', requestPath);
    
    const items = await fs.readdir(dirPath, { withFileTypes: true });
    
    return new Response(JSON.stringify(
      items.map(item => ({
        name: item.name,
        type: item.isDirectory() ? 'directory' : 'file'
      }))
    ), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error reading directory:', error);
    return new Response(JSON.stringify({ error: error.message }), { 
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
}