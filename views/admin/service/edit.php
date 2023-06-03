<?php
$id = $_GET['id'] ?? null;

if ($id === null) {
    redirect('admin/manage?table=service');
}

$db = new Database();
$service = $db->table('service')->where('service_id', $id)->row();

if (isPostMethod()) {
    $result = $db->table('service')
        ->where('service_id', $id)
        ->update([
            'service_type' => $_POST['service_type'],
            'service_title' => $_POST['service_title'],
            'service_description' => $_POST['service_description'],
            'service_image' => $_POST['service_image'],
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
        <form method="post">
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
                <label for="image">Image:</label>
                <input type="text" id="service_image" name="service_image" value="<?php echo $service['service_image']; ?>" required>
            </div>
            
            <button class="button black-button" type="submit">Update Service</button>
        </form>
    </section>
</div>
