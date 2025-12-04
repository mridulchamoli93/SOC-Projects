<?php
/**
 * VULNERABLE dashboard.php (for LOCAL LAB TESTING ONLY)
 * This file intentionally includes insecure patterns to trigger Suricata rules.
 * DO NOT deploy to the internet. Run in an isolated environment.
 */

session_start();
header("X-Lab-Notice: vulnerable-demo");

// ===== Utility =====
function h($s){ return htmlspecialchars($s ?? "", ENT_QUOTES, 'UTF-8'); }
$now = date('Y-m-d H:i:s');

// Unified GET/POST helper
function req($key){ return $_POST[$key] ?? $_GET[$key] ?? null; }

// Ensure uploads dir exists
$uploadDir = __DIR__ . "/uploads";
if (!is_dir($uploadDir)) { @mkdir($uploadDir, 0777, true); }

// ===== Handlers =====

// 1) Reflected XSS
$xssOutput = "";
if (($x = req('xss')) !== null) {
    $xssOutput = $x;
}

// 2) SQLi
$sqlLog = "";
if (req('user_id') !== null || req('query') !== null) {
    $user_id = req('user_id') ?? "";
    $query   = req('query')   ?? "";
    $sql = "SELECT * FROM users WHERE id = '" . $user_id . "'; " . $query;
    $sqlLog = $sql;
}

// 3) Command Injection
$pingOutput = "";
if (($h = req('host')) !== null) {
    $pingOutput = shell_exec("ping -c 1 " . $h);
}

// 4) LFI / Traversal
$lfiOutput = "";
if (($p = req('page')) !== null) {
    $target = $p;
    if (is_file($target)) {
        $lfiOutput = "<pre>" . h(@file_get_contents($target)) . "</pre>";
    } else {
        ob_start();
        @include $target;
        $lfiOutput = ob_get_clean();
        if ($lfiOutput === "") {
            $lfiOutput = "<em>No output from include(). Try another path.</em>";
        }
    }
}

// 5) File Upload
$uploadMsg = "";
if (!empty($_FILES['upload']['name'])) {
    $name = $_FILES['upload']['name'];
    $tmp  = $_FILES['upload']['tmp_name'];
    $dest = $uploadDir . "/" . $name;
    if (@move_uploaded_file($tmp, $dest)) {
        $url = "uploads/" . rawurlencode($name);
        $uploadMsg = "Uploaded: <a href='" . $url . "' target='_blank'>" . h($url) . "</a>";
    } else {
        $uploadMsg = "Upload failed";
    }
}

// 6) Base64
$b64Output = "";
if (($b = req('b64')) !== null) {
    $b64Output = base64_decode($b, true);
    if ($b64Output === false) $b64Output = "Invalid base64 input";
}

// 7) XPath Injection
$xpathOutput = "";
if (($f = req('filter')) !== null) {
    $xpath = "//user[name='{$f}']";
    $xpathOutput = "Simulated XPath: " . $xpath;
}

// 8) Debug Functions
$debugEcho = "";
if (($d = req('debug_hint')) !== null) {
    $debugEcho = $d;
}
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Hacker Dashboard (Lab) - <?=h($now)?></title>
  <style>
    body {
      font-family: "Courier New", monospace;
      margin: 0;
      background: #0d0d0d;
      color: #00ff66;
    }
    header,footer {
      background: #111;
      padding: 16px 20px;
      border-bottom: 1px solid #00ff66;
    }
    header h1 {
      margin: 0;
      font-size: 22px;
      color: #00ff66;
    }
    main {
      padding: 20px;
      display: grid;
      gap: 20px;
      grid-template-columns: repeat(auto-fit,minmax(340px,1fr));
    }
    h2 {
      margin: 0 0 10px;
      color: #00ffaa;
    }
    .card {
      background: #111;
      border: 1px solid #00ff66;
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 0 15px rgba(0,255,102,0.15);
    }
    input,textarea,button {
      width: 100%;
      padding: 10px;
      border-radius: 6px;
      border: 1px solid #00ff66;
      background: #000;
      color: #00ff66;
      font-family: "Courier New", monospace;
    }
    input:focus,textarea:focus {
      outline: none;
      border-color: #00ffaa;
    }
    button {
      cursor: pointer;
      background: #00ff66;
      color: #000;
      font-weight: bold;
      margin-top: 8px;
    }
    button:hover {
      background: #00cc55;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .out {
      background: #000;
      border: 1px dashed #00ff66;
      padding: 10px;
      border-radius: 6px;
      margin-top: 8px;
      min-height: 36px;
      color: #00ff66;
    }
    small {
      opacity: .8;
      display: block;
      margin: 4px 0;
      color: #66ff66;
    }
    a {
      color: #00ffaa;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    footer {
      border-top: 1px solid #00ff66;
      text-align: center;
      font-size: 13px;
      padding: 12px;
      background: #111;
    }
  </style>
</head>
<body>
<header>
  <h1>☠ Hacker Lab Dashboard — LOCAL IDS TESTING ONLY ☠</h1>
  <small>Trigger Suricata rules using <code>/dashboard.php</code>. Supports GET & POST parameters.</small>
</header>

<main>
  <!-- Same vulnerable sections, only styled -->
  <section class="card">
    <h2>1) Reflected XSS</h2>
    <form method="post">
      <textarea name="xss" rows="2" placeholder="&lt;script&gt;alert(1)&lt;/script&gt;"></textarea>
      <button>Send</button>
    </form>
    <small>Try: <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></small>
    <div class="out"><?= $xssOutput ?: "<em>Awaiting input…</em>" ?></div>
  </section>

  <section class="card">
    <h2>2) SQLi</h2>
    <form method="post">
      <input name="user_id" placeholder="1' OR '1'='1 -- " />
      <input name="query" placeholder="UNION SELECT 1,2,3; SLEEP(5);" />
      <button>Run</button>
    </form>
    <small>Example: <code>/dashboard.php?user_id=1' OR '1'='1</code></small>
    <div class="out"><pre><?= h($sqlLog ?: "Enter payloads…") ?></pre></div>
  </section>

  <section class="card">
    <h2>3) Command Injection</h2>
    <form method="post">
      <input name="host" placeholder="127.0.0.1; id; whoami; cat /etc/passwd" />
      <button>Ping</button>
    </form>
    <div class="out"><pre><?= h($pingOutput ?: "Output appears here…") ?></pre></div>
  </section>

  <section class="card">
    <h2>4) Local File Inclusion</h2>
    <form method="post">
      <input name="page" placeholder="../../../../etc/passwd" />
      <button>Include</button>
    </form>
    <div class="out"><?= $lfiOutput ?: "<em>Try including a file path…</em>" ?></div>
  </section>

  <section class="card">
    <h2>5) File Upload</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="upload" />
      <button>Upload</button>
    </form>
    <small>Upload <code>shell.php</code> → accessible under <code>uploads/</code></small>
    <div class="out"><?= $uploadMsg ?: "<em>Upload a file…</em>" ?></div>
  </section>

  <section class="card">
    <h2>6) Base64 Payload</h2>
    <form method="post">
      <textarea name="b64" rows="2" placeholder="U29tZSBiYXNlNjQgc3RyaW5n"></textarea>
      <button>Decode</button>
    </form>
    <div class="out"><pre><?= h($b64Output ?: "Decoded output…") ?></pre></div>
  </section>

  <section class="card">
    <h2>7) XPath Injection</h2>
    <form method="post">
      <input name="filter" placeholder="' or count(*) or '1'='1" />
      <button>Filter</button>
    </form>
    <div class="out"><?= h($xpathOutput ?: "Builds a fake XPath…") ?></div>
  </section>

  <section class="card">
    <h2>8) Debug Functions</h2>
    <form method="post">
      <input name="debug_hint" placeholder="phpinfo(); system('id'); eval($_GET['x']);" />
      <button>Echo</button>
    </form>
    <div class="out"><pre><?= h($debugEcho ?: "Any text echoed here…") ?></pre></div>
  </section>

  <section class="card">
    <h2>9) Evil.com Tests</h2>
    <p>
      <a href="http://evil.com" target="_blank">Go to evil.com</a><br/>
      <a href="/dashboard.php?referer=http://evil.com">Send Referrer</a><br/>
      <a href="http://evil.com/malware.exe" target="_blank">Download from evil.com</a>
    </p>
    <small>Use these to trigger <code>http.host</code>, <code>http.referer</code>, and download rules.</small>
  </section>
</main>

<footer>
  <p>© Hacker Lab Dashboard — IDS testing only. <strong>Never deploy in production.</strong></p>
</footer>
</body>
</html>
