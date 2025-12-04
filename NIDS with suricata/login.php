<?php
session_start();

// DB connection
$servername = "localhost";
$username = "hacklab";
$password = "hackpass";
$dbname = "hacklab";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$flash = "";

// 🔥 Merge GET + POST (so script handles ?user=...&pass=... as well)
$request = array_merge($_GET, $_POST);

// Handle login (intentionally vulnerable to SQLi)
if (isset($request['login']) || (isset($request['user']) && isset($request['pass']))) {
    // Accept both styles: username/password (form) or user/pass (query)
    $user = isset($request['username']) ? $request['username'] : (isset($request['user']) ? $request['user'] : "");
    $pass = isset($request['password']) ? $request['password'] : (isset($request['pass']) ? $request['pass'] : "");

    $sql = "SELECT * FROM users WHERE username='$user' AND password='$pass'";
    $result = $conn->query($sql);

    if ($result && $result->num_rows > 0) {
        // ✅ Set session BEFORE redirect so dashboard gate works
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $user;
        header("Location: dashboard.php");
        exit();
    } else {
        $flash = "<div class='msg error' id='flash'>❌ Invalid credentials</div>";
    }
}

// Handle register (also intentionally insecure: no hashing/validation)
if (isset($request['register'])) {
    $newuser = $request['new_username'];
    $newpass = $request['new_password'];
    $sql = "INSERT INTO users (username, password) VALUES ('$newuser', '$newpass')";
    if ($conn->query($sql) === TRUE) {
        $flash = "<div class='msg success' id='flash'>✅ User registered successfully! Please log in.</div>";
    } else {
        $flash = "<div class='msg error' id='flash'>❌ Error: " . $conn->error . "</div>";
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>💻 Mridul Hacklabs - Login</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Fira+Code&display=swap" rel="stylesheet">
<style>
  :root{
    --neon: #00ff88;   /* branding color */
    --bg1:  rgba(0,255,150,0.16);
    --bg2:  rgba(255,0,255,0.16);
  }
  *{box-sizing:border-box}
  body{
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:'Fira Code', monospace;
    color:#eee;
    background:#0d0d0d;
    overflow:hidden;
  }
  /* Matrix background */
  canvas{
    position:fixed;
    inset:0;
    z-index:-2;
  }
  /* Neon gradient overlay */
  .overlay{
    position:fixed;
    inset:0;
    background:
      radial-gradient(circle at 25% 30%, var(--bg1), transparent 60%),
      radial-gradient(circle at 80% 70%, var(--bg2), transparent 60%);
    z-index:-1;
  }

  .card{
    width: 520px;           /* bigger box */
    max-width: 92vw;
    background: rgba(20,20,40,0.92);
    border-radius:18px;
    padding:44px 36px;
    text-align:center;
    box-shadow: 0 0 34px rgba(0,255,150,0.35), inset 0 0 0 1px rgba(255,255,255,0.05);
    animation: floaty 5s ease-in-out infinite;
    backdrop-filter: blur(3px);
  }
  @keyframes floaty{
    0%,100%{ transform: translateY(0) }
    50%{ transform: translateY(-7px) }
  }
  h1{
    margin:0 0 16px;
    font-family:'Orbitron', sans-serif;
    font-size:28px;
    letter-spacing:0.5px;
    color: var(--neon);                /* 💻 Mridul Hacklabs color */
    text-shadow: 0 0 14px rgba(0,255,136,0.65);
  }
  p.sub{
    margin:0 0 18px;
    opacity:0.8;
    font-size:13px;
  }
  form{
    margin:0;
  }
  .group{
    margin:12px auto;
    width:100%;
  }
  input[type="text"], input[type="password"]{
    width:100%;
    padding:14px 14px;
    border:none;
    border-radius:10px;
    background:#131313;
    color:#fff;
    font-size:15px;
    outline:none;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
  }
  .btn{
    width:100%;
    padding:13px 16px;
    border:none;
    border-radius:10px;
    margin-top:12px;
    font-weight:700;
    font-size:16px;
    cursor:pointer;
    background: var(--neon);
    color:#07130c;
    box-shadow: 0 0 18px rgba(0,255,136,0.35);
    transition: transform .06s ease, filter .2s ease;
  }
  .btn:hover{ filter:brightness(0.95) }
  .btn:active{ transform: translateY(1px) }

  .switcher{
    margin-top:14px;
    color:#8fdfff;
    text-decoration:underline;
    cursor:pointer;
    user-select:none;
  }

  .msg{
    margin: 10px 0 18px;
    padding:10px 12px;
    border-radius:10px;
    font-weight:700;
    font-size:14px;
    animation: pop .18s ease;
  }
  @keyframes pop{ from{transform:scale(.98);opacity:.6} to{transform:scale(1);opacity:1} }
  .success{ color: var(--neon); background: rgba(0,255,136,0.10); }
  .error  { color: #ff5a5a;   background: rgba(255, 0, 0, 0.10); }

  .hidden{ display:none }
</style>
</head>
<body>
  <div class="overlay"></div>
  <canvas id="matrix"></canvas>

  <div class="card">
    <h1>💻 Mridul Hacklabs</h1>
    <p class="sub">Intentionally vulnerable login for NIDS testing. Do not use in production.</p>

    <?php if (!empty($flash)) echo $flash; ?>

    <!-- Login -->
    <form id="loginForm" method="POST">
      <div class="group">
        <input type="text" name="username" placeholder="👤 Username" required>
      </div>
      <div class="group">
        <input type="password" name="password" placeholder="🔑 Password" required>
      </div>
      <button class="btn" type="submit" name="login" value="1">Login</button>
    </form>

    <!-- Register -->
    <form id="registerForm" method="POST" class="hidden">
      <div class="group">
        <input type="text" name="new_username" placeholder="👤 New Username" required>
      </div>
      <div class="group">
        <input type="password" name="new_password" placeholder="🔑 New Password" required>
      </div>
      <button class="btn" type="submit" name="register" value="1">Register</button>
    </form>

    <div class="switcher" onclick="toggleForms()">
      ➕ New user? Register here
    </div>
  </div>

<script>
  // Toggle login/register forms + switcher text
  function toggleForms(){
    const login = document.getElementById('loginForm');
    const reg   = document.getElementById('registerForm');
    const sw    = document.querySelector('.switcher');
    const loginHidden = login.classList.contains('hidden');
    login.classList.toggle('hidden');
    reg.classList.toggle('hidden');
    sw.textContent = loginHidden ? '↩ Already have an account? Back to Login' : '➕ New user? Register here';
  }

  // Auto-hide flash message after 5s
  (function(){
    const f = document.getElementById('flash');
    if (f){
      setTimeout(()=>{ f.style.display='none'; }, 5000);
    }
  })();

  // Matrix background animation
  (function(){
    const canvas = document.getElementById('matrix');
    const ctx = canvas.getContext('2d');

    function resize(){
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      cols = Math.floor(canvas.width / fontSize);
      drops = Array(cols).fill(1);
    }

    const glyphs = "01#@%&$*";
    const letters = glyphs.split("");
    const fontSize = 14;
    let cols = 0;
    let drops = [];

    window.addEventListener('resize', resize, {passive:true});
    resize();

    function draw(){
      // trail
      ctx.fillStyle = "rgba(0,0,0,0.06)";
      ctx.fillRect(0,0,canvas.width,canvas.height);

      ctx.fillStyle = "#0f0";
      ctx.font = fontSize + "px monospace";

      for (let i=0; i<drops.length; i++){
        const text = letters[Math.floor(Math.random()*letters.length)];
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);

        if (drops[i]*fontSize > canvas.height && Math.random() > 0.975){
          drops[i] = 1;
        }
        drops[i]+=0.4;
      }
      requestAnimationFrame(draw);
    }
    draw();
  })();
</script>
</body>
</html>
