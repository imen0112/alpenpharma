<?php
// Partnership enquiry handler, hosted on the Ooredoo cPanel at https://alpen-health.com/contact.php.
// The site itself runs on Railway (www.alpen-health.com) and posts here cross-origin.
// Answers JSON to fetch() requests, redirects otherwise. Kept compatible with PHP 7.0.

const RECIPIENT = 'info@alpen-health.com';
const SENDER = 'website@alpen-health.com';
const SITE = 'https://www.alpen-health.com';

$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
if (in_array($origin, [SITE, 'https://alpen-health.com'], true)) {
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Vary: Origin');
}
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Methods: POST');
    header('Access-Control-Allow-Headers: Accept, Content-Type');
    exit;
}

$accept = isset($_SERVER['HTTP_ACCEPT']) ? $_SERVER['HTTP_ACCEPT'] : '';
$wantsJson = strpos($accept, 'application/json') !== false;

function reply($ok, $error = '')
{
    global $wantsJson;
    if ($wantsJson) {
        header('Content-Type: application/json');
        http_response_code($ok ? 200 : 400);
        echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error]);
    } else {
        header('Location: ' . SITE . '/contact.html?sent=' . ($ok ? '1' : '0'));
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ' . SITE . '/contact.html');
    exit;
}

// Honeypot: bots fill the hidden field
if (!empty($_POST['website'])) {
    reply(true);
}

function cut($v, $max)
{
    return function_exists('mb_substr') ? mb_substr($v, 0, $max, 'UTF-8') : substr($v, 0, $max);
}

function field($key, $max = 200)
{
    $v = trim((string)(isset($_POST[$key]) ? $_POST[$key] : ''));
    $v = str_replace(["\r", "\n"], ' ', $v);
    return cut($v, $max);
}

$data = [
    'Company'   => field('company'),
    'Name'      => field('name'),
    'Position'  => field('position'),
    'Email'     => field('email'),
    'Market'    => field('market'),
    'Therapeutic area' => field('area'),
    'Portfolio / opportunity' => field('portfolio'),
];
$message = cut(trim((string)(isset($_POST['message']) ? $_POST['message'] : '')), 5000);

if ($data['Company'] === '' || $data['Name'] === '' || $data['Market'] === '' || $message === '') {
    reply(false, 'Please complete all required fields.');
}
if (!filter_var($data['Email'], FILTER_VALIDATE_EMAIL)) {
    reply(false, 'Please enter a valid email address.');
}
if ((isset($_POST['consent']) ? $_POST['consent'] : '') !== 'yes') {
    reply(false, 'Please accept the privacy notice.');
}

$body = "New partnership enquiry from alpen-health.com\n\n";
foreach ($data as $label => $value) {
    $body .= str_pad($label . ':', 26) . ($value !== '' ? $value : '-') . "\n";
}
$body .= "\nMessage:\n" . $message . "\n\n---\nSent " . date('Y-m-d H:i') . ' from '
    . (isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '') . "\n";

$subject = '=?UTF-8?B?' . base64_encode('Partnership enquiry: ' . $data['Company']) . '?=';
$headers = [
    'From: Alpen Health Website <' . SENDER . '>',
    'Reply-To: ' . $data['Email'],
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = mail(RECIPIENT, $subject, $body, implode("\r\n", $headers), '-f' . SENDER);
reply($sent, $sent ? '' : 'The message could not be sent. Please write to info@alpen-health.com.');
