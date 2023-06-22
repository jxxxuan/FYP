 <?php
require_once 'constant.php';
/**
 * Load view
 *
 * @param string $view
 * @return string
 */
function getView($view)
{
    return APPPATH . 'views' . DIRECTORY_SEPARATOR . str_replace('.', DIRECTORY_SEPARATOR, $view) . '.php';
}

/**
 * Get relative route URL
 *
 * @param string $route
 * @return string
 */
function route($path = '', $id = null)
{
    $path = trim($path, '/');

    $route = BASEPATH . '/' . trim($path, '/');

    if ($id !== null) {
        $route .= '?id=' . $id;
    }
    return $route;
}

/**
 * Get relative asset URL
 *
 * @param string $url
 * @return string
 */
function asset($url)
{
    return BASEPATH . '/' . ltrim($url, '/');
}

/**
 * Redirect 
 *
 * @param string $to
 * @return void
 */
function redirect($to = null,$id=null)
{
	$route = BASEPATH . '/' . ltrim($to, '/');
	if ($id !== null) {
        $route .= '?id=' . $id;
    }
	
    header('Location: ' . $route);
    http_response_code(302);
    exit();
}

/**
 * Check server is handling post method
 *
 * @return bool
 */
function isPostMethod()
{
    return $_SERVER['REQUEST_METHOD'] === 'POST';
}

/**
 * Get session data
 *
 * @param string $key
 * @param array|float|int|string|null $default
 * @return array|float|int|string|null
 */
function getSession($key, $default = null)
{
    return $_SESSION[$key] ?? $default;
}

/**
 * Set session data
 *
 * @param array|string $key
 * @param array|float|int|string|null $value
 * @return void
 */
function setSession($key, $value = null)
{
    if (is_array($key)) {
        foreach ($key as $keyName => $keyValue) {
            setSession($keyName, $keyValue);
        }
        return;
    }

    $_SESSION[$key] = $value;
}

/**
 * Set flash into session variable for temparary use
 *
 * @param string $key
 * @param array|float|int|string|null $value
 * @return void
 */
function setFlash($key, $value)
{
    if (!isset($_SESSION['flash'])) {
        $_SESSION['flash'] = [];
    }

    $_SESSION['flash'][$key] = $value;
}

/**
 * Get flash from session variable
 *
 * @return array|float|int|string|null
 */
function getFlash($key)
{
    $value = $_SESSION['flash'][$key] ?? null;

    unset($_SESSION['flash'][$key]);

    return $value;
}

/**
 * Determine if user is loggedin
 *
 * @param int $userRole
 * @return bool
 */
function authenticated($userRole = null)
{
    $loggedin = getSession('loggedin', false);

    if ($loggedin && $userRole !== null) {
        return getSession('user_role') === $userRole;
    }

    return $loggedin;
}