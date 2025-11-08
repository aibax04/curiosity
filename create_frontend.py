from pathlib import Path

# Minimalist black and white UI
frontend_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Web App Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #000;
            color: #fff;
            min-height: 100vh;
            overflow: hidden;
        }

        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .prompt-section {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            transition: all 0.3s ease;
        }

        .prompt-section.minimized {
            flex: 0 0 70px;
            padding: 1rem 2rem;
            background: #111;
            border-bottom: 1px solid #333;
        }

        .prompt-wrapper {
            max-width: 600px;
            width: 100%;
        }

        .prompt-section.minimized .prompt-wrapper {
            max-width: 100%;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        h1 {
            color: #fff;
            font-size: 2rem;
            font-weight: 300;
            margin-bottom: 0.5rem;
            text-align: center;
            letter-spacing: -0.5px;
        }

        .prompt-section.minimized h1 {
            font-size: 1.2rem;
            margin-bottom: 0;
            text-align: left;
        }

        .subtitle {
            color: #888;
            font-size: 0.95rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 300;
        }

        .prompt-section.minimized .subtitle {
            display: none;
        }

        .input-container {
            position: relative;
            width: 100%;
        }

        .prompt-section.minimized .input-container {
            flex: 1;
        }

        .prompt-input {
            width: 100%;
            padding: 1rem 5rem 1rem 1.5rem;
            font-size: 1rem;
            border: 1px solid #333;
            border-radius: 4px;
            background: #111;
            color: #fff;
            outline: none;
            transition: border-color 0.2s;
        }

        .prompt-input:focus {
            border-color: #666;
        }

        .prompt-section.minimized .prompt-input {
            padding: 0.7rem 4rem 0.7rem 1rem;
            font-size: 0.9rem;
        }

        .generate-btn {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            padding: 0.6rem 1.5rem;
            background: #fff;
            color: #000;
            border: none;
            border-radius: 3px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .generate-btn:hover:not(:disabled) {
            background: #ddd;
        }

        .generate-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .terminal-section {
            display: none;
            background: #0a0a0a;
            border-top: 1px solid #222;
            border-bottom: 1px solid #222;
            margin: 0 2rem;
            padding: 1rem;
            max-height: 250px;
            overflow-y: auto;
        }

        .terminal-section.active {
            display: block;
        }

        .terminal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #222;
        }

        .terminal-title {
            color: #888;
            font-weight: 400;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }

        .terminal-controls {
            display: flex;
            gap: 0.5rem;
        }

        .terminal-btn {
            background: transparent;
            border: 1px solid #333;
            color: #888;
            padding: 0.3rem 0.7rem;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }

        .terminal-btn:hover {
            background: #111;
            color: #fff;
            border-color: #555;
        }

        .terminal-output {
            font-family: 'Courier New', 'Consolas', monospace;
            font-size: 12px;
            line-height: 1.5;
            color: #aaa;
        }

        .terminal-line {
            margin: 1px 0;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .terminal-line.info {
            color: #fff;
        }

        .terminal-line.success {
            color: #6c6;
        }

        .terminal-line.warning {
            color: #fc6;
        }

        .terminal-line.error {
            color: #f66;
        }

        .connection-status {
            display: inline-block;
            padding: 0.15rem 0.4rem;
            border-radius: 2px;
            font-size: 0.7rem;
            font-weight: 400;
            margin-left: 0.5rem;
        }

        .connection-status.connected {
            background: #1a1a1a;
            color: #6c6;
            border: 1px solid #333;
        }

        .connection-status.disconnected {
            background: #1a1a1a;
            color: #f66;
            border: 1px solid #333;
        }

        .loading {
            display: none;
            text-align: center;
            color: #888;
            margin-top: 2rem;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 2px solid #222;
            border-top: 2px solid #fff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .split-view {
            flex: 1;
            display: none;
            opacity: 0;
        }

        .split-view.active {
            display: flex;
            animation: fadeIn 0.3s ease forwards;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        .panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0a0a0a;
            margin: 1rem;
            border: 1px solid #222;
            overflow: hidden;
        }

        .panel-header {
            padding: 0.8rem 1.2rem;
            background: #111;
            color: #fff;
            font-weight: 400;
            font-size: 0.9rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #222;
        }

        .panel-tools {
            display: flex;
            gap: 0.5rem;
        }

        .tool-btn {
            background: transparent;
            border: 1px solid #333;
            color: #888;
            padding: 0.3rem 0.7rem;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }

        .tool-btn:hover {
            background: #1a1a1a;
            color: #fff;
            border-color: #555;
        }

        .panel-content {
            flex: 1;
            overflow: auto;
        }

        .code-editor {
            width: 100%;
            height: 100%;
            padding: 1.2rem;
            font-family: 'Courier New', 'Consolas', monospace;
            font-size: 13px;
            line-height: 1.6;
            border: none;
            outline: none;
            resize: none;
            background: #0a0a0a;
            color: #ddd;
        }

        .preview-frame {
            width: 100%;
            height: 100%;
            border: none;
            background: #fff;
        }

        .file-tabs {
            display: flex;
            gap: 0;
            padding: 0.5rem 1rem;
            background: #0a0a0a;
            border-bottom: 1px solid #222;
            overflow-x: auto;
        }

        .file-tab {
            padding: 0.4rem 1rem;
            background: transparent;
            border: 1px solid transparent;
            border-bottom: none;
            cursor: pointer;
            font-size: 0.85rem;
            white-space: nowrap;
            transition: all 0.2s;
            color: #666;
        }

        .file-tab:hover {
            color: #aaa;
            background: #111;
        }

        .file-tab.active {
            background: #111;
            color: #fff;
            border-color: #333 #333 transparent #333;
        }

        .status-bar {
            padding: 0.4rem 1rem;
            background: #0a0a0a;
            border-top: 1px solid #222;
            font-size: 0.8rem;
            color: #666;
            display: flex;
            justify-content: space-between;
        }

        .error-message {
            background: #1a0000;
            border: 1px solid #330000;
            color: #ff6666;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 3px;
            display: none;
            white-space: pre-wrap;
            font-size: 0.85rem;
        }

        .error-message.active {
            display: block;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }

        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="prompt-section" id="promptSection">
            <div class="prompt-wrapper">
                <h1>AI Web App Generator</h1>
                <p class="subtitle">Enter a description to generate your application</p>
                
                <div class="input-container">
                    <input 
                        type="text" 
                        class="prompt-input" 
                        id="promptInput"
                        placeholder="Build a colorful modern todo app"
                    >
                    <button class="generate-btn" id="generateBtn">Generate</button>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating application...</p>
                </div>

                <div class="error-message" id="errorMessage"></div>
            </div>
        </div>

        <div class="terminal-section" id="terminalSection">
            <div class="terminal-header">
                <div class="terminal-title">
                    TERMINAL OUTPUT
                    <span class="connection-status disconnected" id="connectionStatus">Disconnected</span>
                </div>
                <div class="terminal-controls">
                    <button class="terminal-btn" id="clearTerminalBtn">Clear</button>
                    <button class="terminal-btn" id="toggleTerminalBtn">Hide</button>
                </div>
            </div>
            <div class="terminal-output" id="terminalOutput"></div>
        </div>

        <div class="split-view" id="splitView">
            <div class="panel">
                <div class="panel-header">
                    <span>Code Editor</span>
                    <div class="panel-tools">
                        <button class="tool-btn" id="copyBtn">Copy</button>
                        <button class="tool-btn" id="downloadBtn">Download</button>
                    </div>
                </div>
                <div class="file-tabs" id="fileTabs"></div>
                <div class="panel-content">
                    <textarea class="code-editor" id="codeEditor" spellcheck="false"></textarea>
                </div>
                <div class="status-bar">
                    <span id="fileInfo">No file selected</span>
                    <span id="lineInfo">Lines: 0</span>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span>Live Preview</span>
                    <div class="panel-tools">
                        <button class="tool-btn" id="refreshBtn">Refresh</button>
                    </div>
                </div>
                <div class="panel-content">
                    <iframe class="preview-frame" id="previewFrame"></iframe>
                </div>
            </div>
        </div>
    </div>

    <script>
        const state = { 
            files: {}, 
            currentFile: null,
            ws: null,
            isGenerating: false
        };
        
        const promptSection = document.getElementById('promptSection');
        const promptInput = document.getElementById('promptInput');
        const generateBtn = document.getElementById('generateBtn');
        const loading = document.getElementById('loading');
        const splitView = document.getElementById('splitView');
        const codeEditor = document.getElementById('codeEditor');
        const previewFrame = document.getElementById('previewFrame');
        const fileTabs = document.getElementById('fileTabs');
        const fileInfo = document.getElementById('fileInfo');
        const lineInfo = document.getElementById('lineInfo');
        const errorMessage = document.getElementById('errorMessage');
        const terminalSection = document.getElementById('terminalSection');
        const terminalOutput = document.getElementById('terminalOutput');
        const connectionStatus = document.getElementById('connectionStatus');
        const clearTerminalBtn = document.getElementById('clearTerminalBtn');
        const toggleTerminalBtn = document.getElementById('toggleTerminalBtn');

        function connectWebSocket() {
            console.log('Connecting to WebSocket...');
            state.ws = new WebSocket('ws://localhost:8000/ws');
            
            state.ws.onopen = () => {
                console.log('WebSocket connected');
                connectionStatus.textContent = 'Connected';
                connectionStatus.className = 'connection-status connected';
                addTerminalLine('Connected to backend server', 'success');
            };
            
            state.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'connection') {
                    addTerminalLine(data.message, 'info');
                } else if (data.type === 'log') {
                    addTerminalLine(data.message, 'log');
                } else if (data.type === 'info') {
                    addTerminalLine(data.message, 'info');
                } else if (data.type === 'success') {
                    addTerminalLine(data.message, 'success');
                } else if (data.type === 'warning') {
                    addTerminalLine(data.message, 'warning');
                } else if (data.type === 'error') {
                    addTerminalLine(data.message, 'error');
                }
            };
            
            state.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                connectionStatus.textContent = 'Error';
                connectionStatus.className = 'connection-status disconnected';
            };
            
            state.ws.onclose = () => {
                console.log('WebSocket disconnected');
                connectionStatus.textContent = 'Disconnected';
                connectionStatus.className = 'connection-status disconnected';
                
                if (!state.isGenerating) {
                    setTimeout(connectWebSocket, 3000);
                }
            };
        }

        function addTerminalLine(text, type = 'log') {
            const line = document.createElement('div');
            line.className = `terminal-line ${type}`;
            line.textContent = text;
            terminalOutput.appendChild(line);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }

        function clearTerminal() {
            terminalOutput.innerHTML = '';
        }

        function toggleTerminal() {
            terminalSection.classList.toggle('active');
            toggleTerminalBtn.textContent = terminalSection.classList.contains('active') ? 'Hide' : 'Show';
        }

        generateBtn.addEventListener('click', handleGenerate);
        promptInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleGenerate();
        });
        codeEditor.addEventListener('input', handleCodeChange);
        document.getElementById('copyBtn').addEventListener('click', copyCode);
        document.getElementById('downloadBtn').addEventListener('click', downloadCode);
        document.getElementById('refreshBtn').addEventListener('click', updatePreview);
        clearTerminalBtn.addEventListener('click', clearTerminal);
        toggleTerminalBtn.addEventListener('click', toggleTerminal);

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.classList.add('active');
            setTimeout(() => {
                errorMessage.classList.remove('active');
            }, 8000);
        }

        async function handleGenerate() {
            const prompt = promptInput.value.trim();
            if (!prompt) {
                showError('Please enter a prompt');
                return;
            }

            state.isGenerating = true;
            generateBtn.disabled = true;
            loading.classList.add('active');
            errorMessage.classList.remove('active');
            
            terminalSection.classList.add('active');
            clearTerminal();
            addTerminalLine('Starting generation process...', 'info');
            addTerminalLine('Sending request to backend...', 'log');

            try {
                console.log('Sending request to backend...');
                console.log('Prompt:', prompt);
                
                const response = await fetch('http://localhost:8000/api/generate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ user_prompt: prompt })
                });

                console.log('Response received');
                console.log('Response status:', response.status);
                console.log('Response ok:', response.ok);

                addTerminalLine('Response received from backend: ' + response.status, 'log');

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Error response:', errorText);
                    throw new Error('Backend error (' + response.status + '): ' + errorText);
                }

                const data = await response.json();
                console.log('Data parsed successfully');
                console.log('Files in response:', Object.keys(data.files || {}).length);
                console.log('Response data:', data);
                
                addTerminalLine('Data received, processing files...', 'log');
                
                if (data.files && Object.keys(data.files).length > 0) {
                    console.log('Files found:', Object.keys(data.files));
                    state.files = data.files;
                    renderFileTabs();
                    const firstFile = Object.keys(state.files)[0];
                    selectFile(firstFile);
                    
                    loading.classList.remove('active');
                    promptSection.classList.add('minimized');
                    splitView.classList.add('active');
                    
                    addTerminalLine('Files loaded in editor successfully', 'success');
                } else {
                    console.warn('No files in response');
                    showError('No files were generated. Please try again.');
                    addTerminalLine('No files were generated', 'warning');
                }
            } catch (error) {
                console.error('Generation error:', error);
                console.error('Error stack:', error.stack);
                
                const errorMsg = error.message || 'Unknown error';
                showError(errorMsg + '\n\nMake sure the backend is running on http://localhost:8000');
                addTerminalLine('Error: ' + errorMsg, 'error');
                
                if (error.stack) {
                    console.error('Full error:', error.stack);
                }
            } finally {
                loading.classList.remove('active');
                generateBtn.disabled = false;
                state.isGenerating = false;
            }
        }

        function renderFileTabs() {
            fileTabs.innerHTML = '';
            Object.keys(state.files).forEach(filename => {
                const tab = document.createElement('div');
                tab.className = 'file-tab';
                tab.textContent = filename;
                tab.addEventListener('click', () => selectFile(filename));
                fileTabs.appendChild(tab);
            });
        }

        function selectFile(filename) {
            state.currentFile = filename;
            codeEditor.value = state.files[filename] || '';
            
            document.querySelectorAll('.file-tab').forEach(tab => {
                tab.classList.toggle('active', tab.textContent === filename);
            });

            updateFileInfo();
            updatePreview();
        }

        function handleCodeChange() {
            if (state.currentFile) {
                state.files[state.currentFile] = codeEditor.value;
                updateFileInfo();
                updatePreview();
            }
        }

        function updateFileInfo() {
            if (state.currentFile) {
                const lines = codeEditor.value.split('\\n').length;
                fileInfo.textContent = state.currentFile;
                lineInfo.textContent = 'Lines: ' + lines;
            }
        }

        function updatePreview() {
            const htmlFile = Object.keys(state.files).find(f => f.endsWith('.html'));
            if (!htmlFile) return;

            let html = state.files[htmlFile];
            const cssFile = Object.keys(state.files).find(f => f.endsWith('.css'));
            const jsFile = Object.keys(state.files).find(f => f.endsWith('.js'));

            if (cssFile && state.files[cssFile]) {
                html = html.replace('</head>', '<style>' + state.files[cssFile] + '</style></head>');
            }
            if (jsFile && state.files[jsFile]) {
                html = html.replace('</body>', '<script>' + state.files[jsFile] + '<\\/script></body>');
            }

            const blob = new Blob([html], { type: 'text/html' });
            previewFrame.src = URL.createObjectURL(blob);
        }

        function copyCode() {
            if (!state.currentFile) {
                showError('No file selected');
                return;
            }
            navigator.clipboard.writeText(codeEditor.value).then(() => {
                const btn = document.getElementById('copyBtn');
                const originalText = btn.textContent;
                btn.textContent = 'Copied';
                setTimeout(() => btn.textContent = originalText, 2000);
            }).catch(() => {
                codeEditor.select();
                document.execCommand('copy');
            });
        }

        function downloadCode() {
            if (!state.currentFile) {
                showError('No file selected');
                return;
            }
            const blob = new Blob([codeEditor.value], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = state.currentFile;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        console.log('Frontend loaded');
        console.log('Backend API: http://localhost:8000');
        
        connectWebSocket();
    </script>
</body>
</html>
"""

def main():
    """Create frontend directory and save index.html"""
    script_dir = Path(__file__).parent
    frontend_dir = script_dir / "frontend"
    frontend_dir.mkdir(exist_ok=True)
    
    index_path = frontend_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(frontend_html)
    
    print("="*60)
    print("Frontend setup complete")
    print("="*60)
    print(f"Created: {index_path}")
    print(f"Size: {len(frontend_html)} bytes")
    print("\nNext steps:")
    print("   1. Run: python dev.py")
    print("   2. Open: http://localhost:3000")
    print("\nFeatures:")
    print("   - Minimalist black and white design")
    print("   - No emojis, clean interface")
    print("   - Terminal output panel")
    print("   - All original components preserved")
    print("="*60)

if __name__ == "__main__":
    main()