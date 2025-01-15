// Initial debug log
console.log('Script started');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    
    // Get DOM elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    
    // Debug log DOM elements
    console.log('DOM Elements:', {
        chatForm: !!chatForm,
        chatInput: !!chatInput,
        chatContainer: !!chatContainer
    });
    
    // Check if elements exist
    if (!chatForm || !chatInput || !chatContainer) {
        console.error('Required elements not found:', {
            chatForm: !!chatForm,
            chatInput: !!chatInput,
            chatContainer: !!chatContainer
        });
        return;
    }

    // Handle chat form submission
    chatForm.addEventListener('submit', function (event) {
        console.log('Form submit event triggered');
        event.preventDefault();
        
        const message = chatInput.value.trim();
        console.log('Message content:', message);
        
        if (!message) {
            console.log('Empty message detected, returning early');
            return;
        }
        
        chatInput.value = '';
        console.log('Chat input cleared');
        
        // Add user's message to chat
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user-message');
        userMessage.textContent = `You: ${message}`;
        chatContainer.appendChild(userMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        console.log('User message added to chat container');
        
        // Show loading message
        const loadingMessage = document.createElement('div');
        loadingMessage.classList.add('message', 'loading-message');
        loadingMessage.textContent = 'Loading...';
        chatContainer.appendChild(loadingMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        console.log('Loading message added');
        
        // Send the message to the server
        console.log('Attempting to send message to server:', message);
        fetch('/send_message', {  // Changed from template literal to direct path
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ 'message': message }),
        })
        .then((response) => {
            console.log('Server response received:', response);
            if (!response.ok) {
                console.error('Server response not OK:', response.status, response.statusText);
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            console.log('Message sent successfully, received data:', data);
            
            // Remove loading message
            chatContainer.removeChild(loadingMessage);
            console.log('Loading message removed');
            
            // Add messages from chat history
            data.chat_history.forEach((msg, index) => {
                console.log(`Adding message ${index + 1} from chat history:`, msg);
                const newMessage = document.createElement('div');
                newMessage.classList.add('message');
                if (msg.startsWith('You:')) {
                    newMessage.classList.add('user-message');
                } else {
                    newMessage.classList.add('app-message');
                }
                newMessage.textContent = msg;
                chatContainer.appendChild(newMessage);
            });
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
            console.log('Chat container scrolled to bottom');
        })
        .catch((error) => {
            console.error('Detailed error information:', {
                message: error.message,
                stack: error.stack,
                error: error
            });
            
            // Remove loading message
            chatContainer.removeChild(loadingMessage);
            console.log('Loading message removed after error');
            
            // Show error message
            const errorMessage = document.createElement('div');
            errorMessage.classList.add('message', 'error-message');
            errorMessage.textContent = 'Error: Unable to send message. Please try again.';
            chatContainer.appendChild(errorMessage);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            console.log('Error message displayed to user');
        });
    });
});