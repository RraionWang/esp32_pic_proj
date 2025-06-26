function checkStatus() {
  fetch("/status")
    .then(res => res.json())
    .then(data => {
      const statusBar = document.getElementById("status-bar");
      const statusLed = document.getElementById("status-led");
      const downloadBtn = document.getElementById("download-btn");

      if (data.exported) {
        statusBar.textContent = "✅ ESP-IDF 环境已初始化";
        statusBar.style.color = "green";
      } else {
        statusBar.textContent = "❌ ESP-IDF 环境未初始化";
        statusBar.style.color = "red";
      }

      if (data.elf_exists) {
        statusLed.style.background = "green";
        downloadBtn.disabled = false;
      } else {
        statusLed.style.background = "gray";
        downloadBtn.disabled = true;
      }
    });
}

function updateElfInfo() {
  fetch("/elf-info")
    .then(res => res.json())
    .then(data => {
      document.getElementById("elf-exists").textContent = data.exists ? "是" : "否";
      document.getElementById("elf-size").textContent = data.size || "--";
      document.getElementById("elf-chip").textContent = data.chip || "--";
    });
}

function startBuild() {
  const log = document.getElementById("log");
  const btn = document.getElementById("build-btn");
  log.innerHTML = "";
  btn.disabled = true;

  const eventSource = new EventSource("/build");

  eventSource.onmessage = function (event) {
    log.innerHTML += event.data + "<br>";
    log.scrollTop = log.scrollHeight;

    if (event.data.includes("✅ 构建完成") || event.data.includes("❌ 构建失败")) {
      eventSource.close();
      btn.disabled = false;
      checkStatus();
      updateElfInfo();
    }
  };

  eventSource.onerror = function () {
    eventSource.close();
    btn.disabled = false;
    if (!log.innerHTML.includes("✅ 构建完成")) {
      log.innerHTML += "<br><span style='color:red;'>❌ 构建失败或连接中断。</span><br>";
    }
  };
}

function clearLog() {
  document.getElementById("log").innerHTML = "";
}

function downloadElf() {
  window.location.href = "/download-elf";
}

function flash() {
  fetch("/flash", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      console.log(data.message);
      alert(data.message);
    });
}

checkStatus();
updateElfInfo();
