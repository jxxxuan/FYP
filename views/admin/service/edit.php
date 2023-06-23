<?php
$id = $_GET['id'] ?? null;

if ($id === null) {
    redirect('admin/manage?table=service');
}

$db = new Database();
$service = $db->table('service')->where('service_id', $id)->row();

if (isPostMethod()) {
    // Handle the image upload if a new image is selected
    if (isset($_FILES['service_image']) && $_FILES['service_image']['error'] === UPLOAD_ERR_OK) {
        $image_temp = $_FILES['service_image']['tmp_name'];
        $target_path = 'uploads/service/' . $_FILES['service_image']['name'];
        move_uploaded_file($image_temp, $target_path);

        // Update the service image path in the database
        $service_image = $target_path;
    } else {
        // No new image selected, use the existing image path from the database
        $service_image = $service['service_image'];
    }

    $result = $db->table('service')
        ->where('service_id', $id)
        ->update([
            'service_type' => $_POST['service_type'],
            'service_title' => $_POST['service_title'],
            'service_description' => $_POST['service_description'],
            'service_price' => $_POST['service_price'],
            'service_image' => $service_image
        ]);

    if ($result) {
        setFlash('message', 'Service successfully edited!');
    }

    redirect('admin/manage?table=service');
}

require_once getView('layout.side-bar');
?>

<div class='box profile'>
    <section>
        <form method="post" enctype="multipart/form-data">
            <div class="input-box">
                <label for="type">Type:</label>
                <input type="text" id="service_type" name="service_type" value="<?php echo $service['service_type']; ?>" required>
            </div>
            
            <div class="input-box">
                <label for="title">Title:</label>
                <input type="text" id="service_title" name="service_title" value="<?php echo $service['service_title']; ?>" required>
            </div>
            
            <div class="input-box">
                <label for="description">Description:</label>
                <textarea id="service_description" name="service_description" required><?php echo $service['service_description']; ?></textarea>
            </div>

            <div class="input-box">
                <label for="price">Price: RM</label>
                <input type="number" step="0.01" id="service_price" name="service_price" value="<?php echo $service['service_price']; ?>" required>
            </div>
            
            <div class="input-box">
                <label for="image">Image:</label>
                <img src="<?php echo route($service['service_image']); ?>" alt="Service Image" style="height: 100px; width: 100px;">
                <input type="file" id="service_image" name="service_image" required>
            </div>
            
            <button class="button black-button" type="submit">Update Service</button>
        </form>
    </section>
</div>
