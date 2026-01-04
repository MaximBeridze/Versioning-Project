document.addEventListener("DOMContentLoaded", () => {
  const summarizeBtn = document.getElementById("summarizeBtn");
  const resultDiv = document.getElementById("result");

  summarizeBtn.addEventListener("click", async () => {
    resultDiv.textContent = "Generating summary...";

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      resultDiv.textContent = "Could not find the active tab.";
      return;
    }

    // 1) Ping content script
    const pingOk = await new Promise((resolve) => {
      chrome.tabs.sendMessage(tab.id, { action: "ping" }, (resp) => {
        resolve(Boolean(resp && resp.ok));
      });
    });

    // 2) If ping failed, inject it
    if (!pingOk) {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["contentScript.js"]
      });
    }

    // 3) Now request summary generation
    chrome.tabs.sendMessage(tab.id, { action: "generate" }, (resp) => {
    if (chrome.runtime.lastError) {
        resultDiv.textContent =
        "Cannot reach content script: " + chrome.runtime.lastError.message;
        return;
    }

    // If we got an ack, we’re good — keep "Generating..." until result arrives
    if (!resp || resp.ok !== true) {
        resultDiv.textContent = "Could not start summarization (no ACK).";
    }
    });
  });

  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "result") {
      resultDiv.textContent = message.summary || "No summary returned.";
    }
  });
});
