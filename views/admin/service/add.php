<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();

if (isPostMethod()) {
        // Check if a file was uploaded successfully
    if (isset($_FILES['service_image']) && $_FILES['service_image']['error'] === UPLOAD_ERR_OK) {
        $image_path = $_FILES['service_image']['tmp_name'];

        // Move the uploaded file to a desired location
        $target_path = 'uploads/service/' . $_FILES['service_image']['name'];
        move_uploaded_file($image_path, $target_path);
    } else {
        // Handle error case when file upload fails
        setFlash('message', 'Failed to upload service image!');
        redirect('admin/manage?table=service');
    }

    $result = $db->table('service')->insert([
        'service_type' => $_POST['service_type'],
        'service_title' => $_POST['service_title'],
        'service_description' => $_POST['service_description'],
        'service_price' => $_POST['service_price'],
        'service_image' => $target_path
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
        <form method="post" enctype="multipart/form-data">
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
                <input type="text" id="service_description" name="service_description" required>
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
