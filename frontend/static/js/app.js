"use strict";

const API_BASE = "http://127.0.0.1:8003/api";

const state = {
  token: localStorage.getItem("token"),
  username: localStorage.getItem("username"),
  email: localStorage.getItem("email"),
  activeChatId: null,
  chatHistory: [],
  isLoading: false,
  deleteChatId: null,
};

if (!state.token) {
  window.location.href = "http://127.0.0.1:8003/login";
}

const elements = {
  sidebar:            document.getElementById("sidebar"),
  sidebarToggleBtn:   document.getElementById("sidebarToggleBtn"),
  mobileSidebarBtn:   document.getElementById("mobileSidebarBtn"),
  newChatBtn:         document.getElementById("newChatBtn"),
  chatHistoryList:    document.getElementById("chatHistoryList"),
  historyEmpty:       document.getElementById("historyEmpty"),
  userName:           document.getElementById("userName"),
  userEmail:          document.getElementById("userEmail"),
  userAvatar:         document.getElementById("userAvatar"),
  profileMenuBtn:     document.getElementById("profileMenuBtn"),
  profileDropdown:    document.getElementById("profileDropdown"),
  logoutBtn:          document.getElementById("logoutBtn"),
  messagesContainer:  document.getElementById("messagesContainer"),
  welcomeScreen:      document.getElementById("welcomeScreen"),
  chatWindow:         document.getElementById("chatWindow"),
  messageInput:       document.getElementById("messageInput"),
  sendBtn:            document.getElementById("sendBtn"),
  toast:              document.getElementById("toast"),
  toastMessage:       document.getElementById("toastMessage"),
  toastIcon:          document.getElementById("toastIcon"),
  deleteModal:        document.getElementById("deleteModal"),
  cancelDeleteBtn:    document.getElementById("cancelDeleteBtn"),
  confirmDeleteBtn:   document.getElementById("confirmDeleteBtn"),
  ollamaStatus:       document.getElementById("ollamaStatus"),
  statusDot:          document.getElementById("statusDot"),
  statusText:         document.getElementById("statusText"),
};

async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${state.token}`,
    ...(options.headers || {})
  };
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) { logout(); return null; }
  return response;
}

async function sendMessage(messageText, chatId = null) {
  const body = { message: messageText };
  if (chatId) body.chat_id = chatId;
  const response = await apiFetch("/chat/message", {
    method: "POST",
    body: JSON.stringify(body)
  });
  if (!response) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to send message");
  return data;
}

async function fetchChatHistory() {
  const response = await apiFetch("/chat/history");
  if (!response) return [];
  const data = await response.json();
  return Array.isArray(data) ? data : [];
}

async function fetchChat(chatId) {
  const response = await apiFetch(`/chat/${chatId}`);
  if (!response) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to load chat");
  return data;
}

async function deleteChat(chatId) {
  const response = await apiFetch(`/chat/${chatId}`, { method: "DELETE" });
  if (!response) return false;
  return response.ok;
}

async function checkOllamaStatus() {
  try {
    const response = await fetch(`${API_BASE}/chat/status/ollama`);
    const data = await response.json();
    return data.ollama_running;
  } catch { return false; }
}

function toggleWelcomeScreen(show) {
  if (show) {
    elements.welcomeScreen.style.display = "flex";
    elements.messagesContainer.style.display = "none";
  } else {
    elements.welcomeScreen.style.display = "none";
    elements.messagesContainer.style.display = "flex";
  }
}

function renderUserMessage(content) {
  const div = document.createElement("div");
  div.className = "message-group";
  div.innerHTML = `<div class="message-user"><div class="bubble">${escapeHtml(content)}</div></div>`;
  elements.messagesContainer.appendChild(div);
  scrollToBottom();
  return div;
}

function renderAIMessage(content) {
  const div = document.createElement("div");
  div.className = "message-group";
  div.innerHTML = `<div class="message-ai"><div class="ai-avatar">⚡</div><div class="bubble">${formatAIResponse(content)}</div></div>`;
  elements.messagesContainer.appendChild(div);
  scrollToBottom();
  return div;
}

function showTypingIndicator() {
  const div = document.createElement("div");
  div.id = "typingIndicator";
  div.className = "typing-indicator";
  div.innerHTML = `<div class="ai-avatar">⚡</div><div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
  elements.messagesContainer.appendChild(div);
  scrollToBottom();
}

function removeTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) indicator.remove();
}

function renderChatHistory(chats) {
  state.chatHistory = chats;
  elements.chatHistoryList.innerHTML = "";
  if (chats.length === 0) {
    elements.chatHistoryList.appendChild(elements.historyEmpty);
    elements.historyEmpty.style.display = "block";
    return;
  }
  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = `history-item ${chat.id === state.activeChatId ? "active" : ""}`;
    item.dataset.chatId = chat.id;
    item.innerHTML = `
      <span class="history-item-icon">💬</span>
      <span class="history-item-title" title="${escapeHtml(chat.title)}">${escapeHtml(chat.title)}</span>
      <button class="history-item-delete" data-chat-id="${chat.id}" title="Delete">✕</button>
    `;
    item.addEventListener("click", (e) => {
      if (!e.target.classList.contains("history-item-delete")) loadChat(chat.id);
    });
    item.querySelector(".history-item-delete").addEventListener("click", (e) => {
      e.stopPropagation();
      showDeleteModal(chat.id);
    });
    elements.chatHistoryList.appendChild(item);
  });
}

function setActiveChatInSidebar(chatId) {
  document.querySelectorAll(".history-item").forEach(item => {
    item.classList.toggle("active", parseInt(item.dataset.chatId) === chatId);
  });
}

function renderFullChat(chat) {
  elements.messagesContainer.innerHTML = "";
  toggleWelcomeScreen(false);
  chat.messages.forEach(msg => {
    if (msg.role === "user") renderUserMessage(msg.content);
    else renderAIMessage(msg.content);
  });
  scrollToBottom();
}

function renderUserInfo() {
  if (state.username) {
    elements.userName.textContent = state.username;
    elements.userEmail.textContent = state.email || "";
    elements.userAvatar.textContent = state.username.charAt(0).toUpperCase();
  }
}

function renderOllamaStatus(isOnline) {
  if (isOnline) {
    elements.statusDot.className = "status-dot online";
    elements.statusText.textContent = "Online";
  } else {
    elements.statusDot.className = "status-dot offline";
    elements.statusText.textContent = "Ollama offline";
  }
}

async function handleSendMessage() {
  const text = elements.messageInput.value.trim();
  if (!text || state.isLoading) return;
  state.isLoading = true;
  setInputEnabled(false);
  toggleWelcomeScreen(false);
  renderUserMessage(text);
  elements.messageInput.value = "";
  autoResizeTextarea();
  showTypingIndicator();
  try {
    const result = await sendMessage(text, state.activeChatId);
    removeTypingIndicator();
    if (result) {
      state.activeChatId = result.chat_id;
      renderAIMessage(result.ai_message.content);
      const history = await fetchChatHistory();
      renderChatHistory(history);
      setActiveChatInSidebar(state.activeChatId);
    }
  } catch (err) {
    removeTypingIndicator();
    showErrorInChat(err.message);
    showToast("Error: " + err.message, "error");
  } finally {
    state.isLoading = false;
    setInputEnabled(true);
    elements.messageInput.focus();
  }
}

async function loadChat(chatId) {
  if (state.isLoading) return;
  try {
    const chat = await fetchChat(chatId);
    if (chat) {
      state.activeChatId = chat.id;
      renderFullChat(chat);
      setActiveChatInSidebar(chatId);
      if (window.innerWidth <= 768) closeMobileSidebar();
    }
  } catch (err) {
    showToast("Failed to load chat", "error");
  }
}

function startNewChat() {
  state.activeChatId = null;
  elements.messagesContainer.innerHTML = "";
  toggleWelcomeScreen(true);
  setActiveChatInSidebar(null);
  elements.messageInput.focus();
  if (window.innerWidth <= 768) closeMobileSidebar();
}

function showErrorInChat(message) {
  const div = document.createElement("div");
  div.className = "message-group";
  div.innerHTML = `<div class="message-ai"><div class="ai-avatar">⚡</div><div class="bubble" style="border-color:rgba(248,113,113,0.3);color:#f87171;">⚠️ ${escapeHtml(message)}</div></div>`;
  elements.messagesContainer.appendChild(div);
  scrollToBottom();
}

function useSuggestion(text) {
  elements.messageInput.value = text;
  elements.messageInput.focus();
  autoResizeTextarea();
  updateSendButton();
}
window.useSuggestion = useSuggestion;

function showDeleteModal(chatId) {
  state.deleteChatId = chatId;
  elements.deleteModal.classList.add("open");
}

function hideDeleteModal() {
  state.deleteChatId = null;
  elements.deleteModal.classList.remove("open");
}

async function handleConfirmDelete() {
  if (!state.deleteChatId) return;
  const idToDelete = state.deleteChatId;
  hideDeleteModal();
  const success = await deleteChat(idToDelete);
  if (success) {
    if (state.activeChatId === idToDelete) startNewChat();
    const history = await fetchChatHistory();
    renderChatHistory(history);
    showToast("Chat deleted", "success");
  } else {
    showToast("Failed to delete chat", "error");
  }
}

function toggleSidebar() {
  if (window.innerWidth <= 768) {
    const isOpen = elements.sidebar.classList.contains("mobile-open");
    if (isOpen) closeMobileSidebar();
    else openMobileSidebar();
  } else {
    elements.sidebar.classList.toggle("collapsed");
  }
}

function openMobileSidebar() {
  elements.sidebar.classList.add("mobile-open");
  getOrCreateOverlay().classList.add("visible");
}

function closeMobileSidebar() {
  elements.sidebar.classList.remove("mobile-open");
  const overlay = document.querySelector(".sidebar-overlay");
  if (overlay) overlay.classList.remove("visible");
}

function getOrCreateOverlay() {
  let overlay = document.querySelector(".sidebar-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.className = "sidebar-overlay";
    overlay.addEventListener("click", closeMobileSidebar);
    document.body.appendChild(overlay);
  }
  return overlay;
}

function toggleProfileDropdown() {
  elements.profileDropdown.classList.toggle("open");
}

document.addEventListener("click", (e) => {
  if (!elements.profileMenuBtn.contains(e.target) && !elements.profileDropdown.contains(e.target)) {
    elements.profileDropdown.classList.remove("open");
  }
});

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("username");
  localStorage.removeItem("email");
  window.location.href = "http://127.0.0.1:8003/login";
}

let toastTimeout;
function showToast(message, type = "success") {
  const icons = { success: "✓", error: "✕", warning: "⚠" };
  elements.toastIcon.textContent = icons[type] || "✓";
  elements.toastMessage.textContent = message;
  elements.toast.className = `toast ${type} show`;
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => { elements.toast.classList.remove("show"); }, 3500);
}

function setInputEnabled(enabled) {
  elements.messageInput.disabled = !enabled;
  elements.sendBtn.disabled = !enabled;
}

function autoResizeTextarea() {
  const el = elements.messageInput;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 200) + "px";
}

function updateSendButton() {
  const hasText = elements.messageInput.value.trim().length > 0;
  elements.sendBtn.disabled = !hasText || state.isLoading;
}

function scrollToBottom() {
  elements.chatWindow.scrollTop = elements.chatWindow.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function formatAIResponse(text) {
  let escaped = escapeHtml(text);
  escaped = escaped.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => `<pre><code>${code.trim()}</code></pre>`);
  escaped = escaped.replace(/`([^`]+)`/g, "<code>$1</code>");
  escaped = escaped.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  escaped = escaped.replace(/\n(?!<\/code>)/g, "<br>");
  return escaped;
}

async function init() {
  renderUserInfo();
  toggleWelcomeScreen(true);
  try {
    const history = await fetchChatHistory();
    renderChatHistory(history);
  } catch (err) { console.error("Failed to load history:", err); }
  const ollamaOnline = await checkOllamaStatus();
  renderOllamaStatus(ollamaOnline);
  setInterval(async () => {
    const online = await checkOllamaStatus();
    renderOllamaStatus(online);
  }, 30000);
}

elements.sendBtn.addEventListener("click", handleSendMessage);
elements.messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSendMessage(); }
});
elements.messageInput.addEventListener("input", () => { autoResizeTextarea(); updateSendButton(); });
elements.newChatBtn.addEventListener("click", startNewChat);
elements.sidebarToggleBtn.addEventListener("click", toggleSidebar);
elements.mobileSidebarBtn.addEventListener("click", toggleSidebar);
elements.profileMenuBtn.addEventListener("click", (e) => { e.stopPropagation(); toggleProfileDropdown(); });
elements.logoutBtn.addEventListener("click", logout);
elements.cancelDeleteBtn.addEventListener("click", hideDeleteModal);
elements.confirmDeleteBtn.addEventListener("click", handleConfirmDelete);
elements.deleteModal.addEventListener("click", (e) => { if (e.target === elements.deleteModal) hideDeleteModal(); });

init();