// ===================== UTILITY FUNCTIONS =====================
/**
 * Fetches data from a URL and returns the JSON response.
 * @param {string} url - The URL to fetch data from.
 * @returns {Promise<Object|null>} - The JSON response or null if an error occurs.
 */
async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error(`Error fetching ${url}:`, error);
    return null;
  }
}

function copyToClipboard(type) {
  let textToCopy;
  if (type === "response") {
    textToCopy = document.querySelector(".response-card p").innerText;
  } else if (type === "code") {
    textToCopy = document.querySelector(".response-card pre code").innerText;
  }
  navigator.clipboard
    .writeText(textToCopy)
    .then(() => {
      alert("Copied to clipboard!");
    })
    .catch((err) => {
      console.error("Failed to copy: ", err);
    });
}

// ===================== SERVER FUNCTIONS =====================
/**
 * Pings the server to check the connection status.
 * @returns {Promise<Object|null>} - The connection details or null if an error occurs.
 */
const pingServer = () => fetchData("/api/connection");

/**
 * Fetches details about available and active models from the server.
 * @returns {Promise<Object|null>} - The model details or null if an error occurs.
 */
const fetchModelDetails = () => fetchData("/api/connection/stats");

// ===================== DISPLAY FUNCTIONS =====================
/**
 * Displays the server connection details in the specified element.
 * @param {Object|null} connection - The connection details.
 * @param {HTMLElement} element - The element to display the details in.
 */
function displayConnectionDetails(connection, element) {
  if (!element) return console.error("Missing element for connection details.");
  element.innerHTML = connection
    ? `<h3>CONNECTION INFO:</h3>
       <p>Host: ${connection.host || "Unknown"}</p>
       <p>Port: ${connection.port || "Unknown"}</p>
       <p>Status: ${connection.status || "Unknown"} - CONNECTED</p>`
    : "<h3>UNABLE TO CONNECT TO SERVER</h3>";
}

/**
 * Displays the available models in the specified element and updates the model picker dropdown.
 * @param {Object|null} models - The model details.
 * @param {HTMLElement} element - The element to display the details in.
 */
function displayModelDetails(models, element) {
  if (!element) return console.error("Missing element for model details.");
  const modelPicker = document.getElementById("model-picker");
  if (models?.available?.length) {
    let modelHTML = "<h3>MODELS:</h3>";
    let optionsHTML = "";
    models.available.forEach(({ name, model }) => {
      modelHTML += `<p>Name/Model: ${name}/${model}</p>`;
      optionsHTML += `<option value="${model}">${name}</option>`;
    });
    element.innerHTML = modelHTML;
    if (modelPicker) modelPicker.innerHTML = optionsHTML;
  } else {
    element.innerHTML = "<h3>No models found on the server.</h3>";
    if (modelPicker)
      modelPicker.innerHTML =
        "<option value=''>Unable to connect to server</option>";
  }
}

/**
 * Displays the active models in the specified element.
 * @param {Object|null} models - The active model details.
 * @param {HTMLElement} element - The element to display the details in.
 */
function displayActiveModels(models, element) {
  if (!element) return console.error("Missing element for active models.");
  if (models?.active?.length) {
    let html = "<h3>ACTIVE MODELS:</h3>";
    models.active.forEach(({ name, model }) => {
      html += `<p>Name/Model: ${name}/${model}</p>`;
    });
    element.innerHTML = html;
  } else {
    element.innerHTML = "<h3>Currently No Active Models Present.</h3>";
  }
}

// ===================== LOADING STATE MANAGEMENT =====================
/**
 * Handles the UI loading state during async operations.
 * @param {Function} func - The async function to execute.
 * @param {number} delay - The delay before re-enabling UI elements.
 * @param {boolean} showLoadingPage - Whether to show a loading page.
 */
async function handleLoadingState(func, delay, showLoadingPage = false) {
  const inputBox = document.getElementById("prompt");
  const inputButton = document.getElementById("prompt-btn");
  const mainContainer = document.getElementById("main");

  if (!mainContainer) return console.error("Missing main container.");

  if (showLoadingPage) mainContainer.innerHTML = "<h1>LOADING...</h1>";
  if (inputBox) inputBox.disabled = true;
  if (inputButton) inputButton.style.display = "none";

  try {
    await func();
  } catch (error) {
    console.error("Error during loading:", error);
    mainContainer.innerHTML = `<h1>ERROR: ${error.message}</h1>`;
  } finally {
    setTimeout(() => {
      if (inputBox) inputBox.disabled = false;
      if (inputButton) inputButton.style.display = "block";
    }, delay);
  }
}

// ===================== PAGE INITIALIZATION =====================
/**
 * Initializes the page by fetching and displaying connection and model details.
 */
async function initializeDataPage() {
  const connectionsInfo = document.getElementById("connectionsInfo");
  const printModel = document.getElementById("print_models");
  const printActiveModel = document.getElementById("print_active_models");

  if (!connectionsInfo || !printModel || !printActiveModel)
    return console.error("One or more required elements not found.");

  const connection = await pingServer();
  const models = await fetchModelDetails();

  displayConnectionDetails(connection, connectionsInfo);
  displayModelDetails(models, printModel);
  displayActiveModels(models, printActiveModel);
}

// ===================== AI COMMUNICATION FUNCTIONS =====================
/**
 * Sends a message to the AI and returns the response.
 * @param {string} prompt - The user's prompt.
 * @param {string} model - The selected model.
 * @returns {Promise<Object>} - The AI's response.
 */
async function sendMessageToAI(prompt, model) {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, model }),
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

/**
 * Displays the AI's response in the specified element.
 * @param {Object} res - The AI's response.
 * @param {HTMLElement} element - The element to display the response in.
 */
function printResponse(res, element) {
  if (!element) return console.error("Missing element for AI response.");
  element.innerHTML = res?.response?.length
    ? `<div class="response-card"><b>AI :</b> ${res.response}</div>`
    : "<h3>No response received.</h3>";
}

/**
 * Handles sending a message to the AI and displaying the response.
 */
async function sendMessage() {
  const modelPicker = document.getElementById("model-picker");
  const prompt = document.getElementById("prompt");
  const inputButton = document.getElementById("prompt-btn");
  const responseContainer = document.getElementById("response-container");

  if (!modelPicker || !prompt || !responseContainer)
    return console.error("Missing required elements for sending message.");

  inputButton.style.display = "none";
  responseContainer.style.display = "block";
  responseContainer.innerHTML = "<h3>LOADING...</h3>";

  try {
    const res = await sendMessageToAI(prompt.value, modelPicker.value);
    printResponse(res, responseContainer);
  } catch (error) {
    console.error("Error sending message:", error);
    responseContainer.innerHTML = "<h3>ERROR SENDING MESSAGE</h3>";
  } finally {
    inputButton.style.display = "block";
  }
}

// ===================== INITIALIZE ON DOM CONTENT LOADED =====================
document.addEventListener("DOMContentLoaded", () => {
  handleLoadingState(initializeDataPage, 1000);
});
