const toggleBtn = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');
const chatContainer = document.getElementById('chat-container')
const chatInput = document.getElementById('chat-input');
const uploadBtn = document.getElementById('UploadBtn');
const fileInput = document.getElementById('file-input');
const sendBtn = document.getElementById('SendBtn');
const newChatBtn = document.getElementById('NewchatBtn');
let file = null;

// Initialize the toggle button position
toggleBtn.style.left = '215px';
toggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('hidden');

    if (sidebar.classList.contains('hidden')) {
        toggleBtn.style.left = '10px';
        chatContainer.classList.add('expanded');

    } else {
        toggleBtn.style.left = '215px';
        chatContainer.classList.remove('expanded');
    }

});

// Auto-resize chat input
chatInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// AutoMatically get access_token from localStorage and include it in the Authorization header for all fetch requests
async function fetchWithAuth(url, options = {}) {
    const access_token = localStorage.getItem("access_token");

    options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${access_token}`
    };

    let response = await fetch(url, options);

    if (response.status === 401) {

        const refresh_token = localStorage.getItem("refresh_token");
        const refreshResponse = await fetch("https://medical-report-analyzer-ai-production.up.railway.app/refresh", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token: refresh_token
            })
        });

        const data = await refreshResponse.json();

        if (refreshResponse.ok) {
            localStorage.setItem("access_token", data.access_token);

            options.headers["Authorization"] = `Bearer ${data.access_token}`;
            response = await fetch(url, options);

        } else {
            alert("Session expired. Please log in again.");
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "login.html";
        }
    }

    return response;
}

uploadBtn.addEventListener('click', async () => {
    fileInput.click();
});

fileInput.addEventListener('change', async () => {
    file = fileInput.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }
    chatInput.value = file.name;
});

function addMessage(text, type) {
    const msg = document.createElement('div');
    msg.classList.add('message', type);

    if (type === 'ai-message') {
        const parsed = marked.parse(text);
        msg.innerHTML = parsed;
    } else {
        msg.textContent = text;
    }

    document.getElementById('chat-messages').appendChild(msg);

    // Hide heading when first message appears
    document.querySelector('h1').style.display = 'none';

    // Switch layout
    document.getElementById('chat-container').classList.add('has-messages');

    msg.scrollIntoView({ behavior: 'smooth' });
}

sendBtn.addEventListener('click', async () => {
    try {
        if (file) {
            addMessage(`📄 ${file.name}`, 'user-message');
            chatInput.value = "";

            const loadingMsg = document.createElement('div');
            loadingMsg.classList.add('message', 'ai-message', 'loading');
            loadingMsg.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
            document.getElementById('chat-messages').appendChild(loadingMsg);
            loadingMsg.scrollIntoView({ behavior: 'smooth' });

            const formData = new FormData();
            formData.append("file", file);

            const response = await fetchWithAuth("https://medical-report-analyzer-ai-production.up.railway.app/summarize/document", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            loadingMsg.remove();

            if (!response.ok) {
                addMessage(`${data.detail}`, 'ai-message');
                return;
            }

            if (data.summary) {
                addMessage(data.summary, 'ai-message');
                file = null;
                fileInput.value = "";
                currentFileId = data.file_id; //  store file_id
                loadUserFiles();
            }

        } else if (chatInput.value.trim() !== "") {

            const message = chatInput.value.trim();

            if (!currentFileId) {
                alert("Please select a file first.");
                return;
            }

            addMessage(message, 'user-message');
            chatInput.value = "";

            const loadingMsg = document.createElement('div');
            loadingMsg.classList.add('message', 'ai-message', 'loading');
            loadingMsg.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
            document.getElementById('chat-messages').appendChild(loadingMsg);
            loadingMsg.scrollIntoView({ behavior: 'smooth' });

            const response = await fetchWithAuth("https://medical-report-analyzer-ai-production.up.railway.app/ask/document", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: message,
                    file_id: currentFileId
                })
            });

            const data = await response.json();
            loadingMsg.remove();

            if (!response.ok) {
                //  backend error → show in chat
                addMessage(`${data.detail}`, 'ai-message');
                return;
            }

            //backend returns answer as plain string
            addMessage(data, 'ai-message');

        } else {
            alert("Please select a file or type a question.");
        }

    } catch (error) {
        console.error("Error caught:", error);
        addMessage("Something went wrong. Try again.", 'ai-message');
    }
});

function resetToNewChat() { 
    document.getElementById('chat-messages').innerHTML = '';
    document.querySelector('h1').style.display = 'block';
    document.getElementById('chat-container').classList.remove('has-messages');
    file = null;
    fileInput.value = "";
    currentFileId = null;
    newChatBtn.scrollIntoView({ behavior: 'smooth' });
};

newChatBtn.addEventListener('click', resetToNewChat);

async function loadUserFiles() {
    try {
        const response = await fetchWithAuth("https://medical-report-analyzer-ai-production.up.railway.app/user/files");
        const files = await response.json();

        const chatList = document.getElementById('chat-list');
        const noChats = document.getElementById('nochats');

        if (!files || files.length === 0) {
            noChats.style.display = 'block';
            return;
        }

        noChats.style.display = 'none';
        chatList.innerHTML = '';

        files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file.filename;
            li.dataset.fileId = file.id;
            li.classList.add('chat-item');

            const delBtn = document.createElement('button');
            delBtn.textContent = 'Delete';
            delBtn.classList.add('delBtn');

            delBtn.addEventListener('click', async (e) => {
                e.stopPropagation();

                if (!confirm("Are you sure you want to delete this file?")) {
                    return;
                }

            try {
                const response = await fetchWithAuth(`https://medical-report-analyzer-ai-production.up.railway.app/delete/files?file_id=${file.id}`, {
                    method: "DELETE"
                });

                if (response.ok) {
                    li.remove(); //  remove from UI even if backend deletion fails
                    alert(`${file.filename} deleted successfully.`);

                    if (Number(currentFileId) === Number(file.id)) {
                        resetToNewChat();
                    }
                } else {
                    alert(`Failed to delete ${file.filename}. Try again.`);
                }

            } catch (error) {
                console.error("Error deleting file:", error);
            }
        });
            li.appendChild(delBtn);
            li.addEventListener('click', () => loadFileChat(file.id));
            chatList.appendChild(li);
    });

    } catch (error) {
        console.error("Error loading files:", error);
    }
}

async function loadFileChat(fileId) {

    try {
        //  Load file summary
        const response = await fetchWithAuth(`https://medical-report-analyzer-ai-production.up.railway.app/files/${fileId}`);
        const data = await response.json();
        console.log("File summary response:", data);

        if (data.summary) {
            document.getElementById('chat-messages').innerHTML = '';
            addMessage(`📄 ${data.filename}`, 'user-message');
            addMessage(data.summary, 'ai-message');
        }

        // Load chat history
        const chatHistoryResponse = await fetchWithAuth(`https://medical-report-analyzer-ai-production.up.railway.app/chat/history/${fileId}`);
        const chatHistory = await chatHistoryResponse.json();

        if (Array.isArray(chatHistory)) {
            chatHistory.forEach(msg => {
                if (msg.role === 'user') {
                    addMessage(msg.content, 'user-message');
                } else if (msg.role === 'model') {
                    addMessage(msg.content, 'ai-message');
                }
            });
        }
    } catch (error) {
        console.error("Error loading file chat:", error);
    }

}

loadUserFiles();