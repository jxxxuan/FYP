<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();

if (isPostMethod()) {
    $result = $db->table('service')->insert([
        'service_type' => $_POST['service_type'],
        'service_title' => $_POST['service_title'],
        'service_description' => $_POST['service_description'],
        'service_price' => $_POST['service_price'],
        'service_image' => $_POST['service_image']
    ]);

    if ($result) {
        setFlash('message', 'Service added successfully!');
    }

    redirect('admin/manage?table=service');
}

require_once getView('layout.side-bar');
?>

<div class="box profile">
    <section>
        <form method="post">
            <div class="input-box">
                <label for="service_type">Service Type:</label>
                <input type="text" id="service_type" name="service_type" required>
            </div>
            <div class="input-box">
                <label for="service_title">Service Title:</label>
                <input type="text" id="service_title" name="service_title" required>
            </div>
            <div class="input-box">
                <label for="service_description">Service Description:</label>
                <textarea id="service_description" name="service_description" required></textarea>
            </div>
            <div class="input-box">
                <label for="service_price">Service Price: RM</label>
                <input type="number" step="0.01" id="service_price" name="service_price" required>
            </div>
            <div class="input-box">
                <label for="service_image">Service Image:</label>
                <input type="file" id="service_image" name="service_image" required>
            </div>
            <button class="button black-button" type="submit">Add Service</button>
        </form>
    </section>
</div>
