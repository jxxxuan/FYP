<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FYP</title>

    <link rel="stylesheet" href="<?php echo asset('css/style.css'); ?>" />
    <style>
        #header-nav {
            margin-left: 1.5rem;
        }
    </style>

    <script src="https://kit.fontawesome.com/e1b9927972.js" crossorigin="anonymous"></script>
</head>

<body class="d-flex flex-column" style="min-height: 100vh;">
    <?php require_once getView('layout.header'); ?>
    <main>
        <?php require_once $main; ?>
    </main>
	
    <?php //require_once getView('layout.footer'); ?>
</body>

</html>