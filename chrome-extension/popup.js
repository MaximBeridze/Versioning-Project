document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("summarizeBtn");
  const result = document.getElementById("result");

  btn.addEventListener("click", () => {
    result.textContent = "Summarize clicked! (Next milestone: call backend and show summary.)";
  });
});
