<?php

define('SMF', 1);
require_once(dirname(__FILE__) . '/Settings.php');
require_once($sourcedir . '/QueryString.php');
require_once($sourcedir . '/Subs.php');
require_once($sourcedir . '/Errors.php');
require_once($sourcedir . '/Load.php');
require_once($sourcedir . '/Security.php');

$smcFunc = array();
loadDatabase();

remove_integration_function('integrate_pre_include', '/var/www/lighttpd/forum/injection.php');
remove_integration_function('integrate_menu_buttons', 'inject_doinject');
add_integration_function('integrate_pre_include', '/var/www/lighttpd/forum/injection.php', TRUE);
add_integration_function('integrate_menu_buttons', 'inject_doinject', TRUE);

?>
