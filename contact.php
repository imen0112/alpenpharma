<?php
// Partnership enquiry handler. Answers JSON to fetch() requests, redirects otherwise.
declare(strict_types=1);

const RECIPIENT = 'info@alpen-health.com';
const SENDER = 'website@alpen-health.com';

$wantsJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');

function reply(bool $ok, string $error = ''): void {
    global $wantsJson;
    if ($wantsJson) {
        header('Content-Type: application/json');
        http_response_code($ok ? 200 : 400);
        echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error]);
    } else {
        header('Location: contact.html?sent=' . ($ok ? '1' : '0'));
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: contact.html');
    exit;
}

// Honeypot: bots fill the hidden field
if (!empty($_POST['website'])) {
    reply(true);
}

function field(string $key, int $max = 200): string {
    $v = trim((string)($_POST[$key] ?? ''));
    $v = str_replace(["\r", "\n"], ' ', $v);
    return mb_substr($v, 0, $max);
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
$message = mb_substr(trim((string)($_POST['message'] ?? '')), 0, 5000);

if ($data['Company'] === '' || $data['Name'] === '' || $data['Market'] === '' || $message === '') {
    reply(false, 'Please complete all required fields.');
}
if (!filter_var($data['Email'], FILTER_VALIDATE_EMAIL)) {
    reply(false, 'Please enter a valid email address.');
}
if (($_POST['consent'] ?? '') !== 'yes') {
    reply(false, 'Please accept the privacy notice.');
}

$body = "New partnership enquiry from alpen-health.com\n\n";
foreach ($data as $label => $value) {
    $body .= str_pad($label . ':', 26) . ($value !== '' ? $value : '-') . "\n";
}
$body .= "\nMessage:\n" . $message . "\n\n---\nSent " . date('Y-m-d H:i') . ' from ' . ($_SERVER['REMOTE_ADDR'] ?? '') . "\n";

$subject = '=?UTF-8?B?' . base64_encode('Partnership enquiry: ' . $data['Company']) . '?=';
$headers = [
    'From: Alpen Health Website <' . SENDER . '>',
    'Reply-To: ' . $data['Email'],
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = mail(RECIPIENT, $subject, $body, implode("\r\n", $headers), '-f' . SENDER);
reply($sent, $sent ? '' : 'The message could not be sent. Please write to info@alpen-health.com.');
