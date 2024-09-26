const notesContainer = document.querySelector(".notes-container");
const createBtn = document.querySelector(".btn");
let userId; // Initialize without a hardcoded value
let username; // Variable to hold the username

// Function to fetch user ID and username from the backend
async function fetchUserInfo() {
    try {
        const response = await fetch("/get_username"); // Endpoint to get username and user_id
        if (response.ok) {
            const data = await response.json();
            userId = data.user_id; // Store user_id
            username = data.username; // Store username
            displayUserName(username); // Call function to display the username
            fetchAndDisplayNotes(); // Fetch notes after getting user info
        } else {
            console.error("Failed to fetch user info.");
        }
    } catch (error) {
        console.error("Error fetching user info:", error);
    }
}

// Function to display the username on the page
function displayUserName(username) {
    const userNameDisplay = document.createElement("div");
    userNameDisplay.className = "username-display"; // Add class for styling if needed
    userNameDisplay.innerText = `Hello, ${username}!`;
    userNameDisplay.style.fontSize = "18px";
    userNameDisplay.style.margin = "10px 0"; // Adjust margin as needed
    document.querySelector(".container").prepend(userNameDisplay); // Add to top of container
}

// Function to fetch and display notes for the user
async function fetchAndDisplayNotes() {
    try {
        const response = await fetch(`/get_notes/${userId}`);
        if (response.ok) {
            const notes = await response.json();
            notes.forEach(note => {
                displayNote(note.id, note.content, note.timestamp);
            });
        } else {
            console.error("Failed to fetch notes.");
        }
    } catch (error) {
        console.error("Error fetching notes:", error);
    }
}

// Function to display a note in the notes container
function displayNote(noteId, content, timestamp) {
    let inputBox = document.createElement("div");
    let img = document.createElement("img");
    let editableArea = document.createElement("div");

    // Format the timestamp text
    let timeString = new Date(timestamp).toLocaleString();
    let timeDiv = document.createElement("div");
    timeDiv.innerText = timeString;
    timeDiv.style.fontSize = "12px";
    timeDiv.style.color = "#888";

    // Styling for the inputBox and editable area
    inputBox.className = "input-box";
    inputBox.style.border = "1px solid #ccc";
    inputBox.style.margin = "10px 0";
    inputBox.style.padding = "10px";
    inputBox.style.position = "relative";

    editableArea.setAttribute("contenteditable", "true");
    editableArea.style.marginTop = "10px";
    editableArea.innerText = content; // Set the content of the note

    img.src = "../static/images/delete.png";
    img.style.float = "right";
    img.style.cursor = "pointer";

    // Append elements
    inputBox.appendChild(timeDiv);
    inputBox.appendChild(img);
    inputBox.appendChild(editableArea);
    notesContainer.appendChild(inputBox);

    // Event listener for updating the note content
    editableArea.addEventListener("blur", function () {
        const newContent = editableArea.innerText;
        if (newContent.trim()) {
            updateNoteInBackend(noteId, newContent); // Call update function
        }
    });

    // Event listener for deleting notes
    img.addEventListener("click", async function () {
        const response = await deleteNoteFromBackend(noteId); // Wait for the delete operation to complete
        if (response.ok) {
            inputBox.remove(); // Only remove the note from the frontend if deletion was successful
        }
    });
}

// Event listener for the create button
createBtn.addEventListener("click", () => {
    let inputBox = document.createElement("div");
    let img = document.createElement("img");
    let timestamp = document.createElement("div");
    let editableArea = document.createElement("div");

    // Get current date and time (used as note id)
    let now = new Date();
    let date = now.toLocaleDateString();
    let time = now.toLocaleTimeString();
    let noteId = `${date} ${time}`;

    // Format the timestamp text
    timestamp.innerText = `${date} ${time}`;
    timestamp.style.fontSize = "12px";
    timestamp.style.color = "#888";

    // Styling for the inputBox and editable area
    inputBox.className = "input-box";
    inputBox.style.border = "1px solid #ccc";
    inputBox.style.margin = "10px 0";
    inputBox.style.padding = "10px";
    inputBox.style.position = "relative";

    editableArea.setAttribute("contenteditable", "true");
    editableArea.style.marginTop = "10px";

    img.src = "../static/images/delete.png";
    img.style.float = "right";
    img.style.cursor = "pointer";

    // Append elements
    inputBox.appendChild(timestamp);
    inputBox.appendChild(img);
    inputBox.appendChild(editableArea);
    notesContainer.appendChild(inputBox);

    // Event listener to send the note data when user clicks outside the note
    document.addEventListener("click", function (e) {
        if (!inputBox.contains(e.target)) {
            // User clicked outside, send data to the backend
            const noteContent = editableArea.innerText;
            if (noteContent.trim()) {
                saveNoteToBackend(noteId, userId, noteContent);
            }
        }
    });
});

// Function to send the note data to the backend
function saveNoteToBackend(noteId, userId, content) {
    fetch("/save_note", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: noteId,
            user_id: userId,
            content: content
        })
    })
    .then(response => {
        if (response.ok) {
            console.log("Note saved successfully!");
        } else {
            console.error("Failed to save note.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

// Function to delete a note from the backend
async function deleteNoteFromBackend(noteId) {
    try {
        const response = await fetch("/delete_note", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: noteId
            })
        });
        if (response.ok) {
            console.log("Note deleted successfully!");
        } else {
            console.error("Failed to delete note.");
        }
        return response; // Return the response
    } catch (error) {
        console.error("Error:", error);
    }
}

// Function to update a note in the backend
function updateNoteInBackend(noteId, content) {
    fetch("/update_note", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: noteId,
            content: content
        })
    })
    .then(response => {
        if (response.ok) {
            console.log("Note updated successfully!");
        } else {
            console.error("Failed to update note.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

// Fetch user info when the script loads
window.onload = fetchUserInfo;
