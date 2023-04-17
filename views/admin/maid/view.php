<?php
$database = new Database();
$maids = $database->table('maid')->rows();
$flash = getFlash('message');
?>

<div class="maid-view-container">
    <div class="maid-view-left ml-3">
        <?php require_once getView('admin.menu'); ?>
    </div>

    <div class="maid-view-right mr-3 pb-3 text-center">
        <h2>MAID LIST</h2>
        <table class="table-container">
            <thead>
                <tr>
                    <th>Maid ID</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Contact</th>
                    <th>Address</th>
                    <th>Experience</th>
                    <th>Availability Start</th>
                    <th>Availability End</th>
                    <th>Skill</th>
                    <th>Email</th>
                </tr>
            </thead>

            <tbody>
                <?php foreach ($maids as $maid) : ?>
                    <tr>
                        <td><?php echo $maid['maid_id']; ?></td>
                        <td><?php echo $maid['name']; ?></td>
                        <td><?php echo $maid['age']; ?></td>
                        <td><?php echo $maid['gender']; ?></td>
                        <td><?php echo $maid['contact']; ?></td>
                        <td><?php echo $maid['address']; ?></td>
                        <td><?php echo $maid['experience']; ?></td>
                        <td><?php echo date('H:i', strtotime($maid['availability_start'])); ?></td>
                        <td><?php echo date('H:i', strtotime($maid['availability_end'])); ?></td>
                        <td><?php echo $maid['skill']; ?></td>
                        <td><?php echo $maid['maid_email']; ?></td>
                        <td><a href="<?php echo route('maid/edit', $maid['maid_id']); ?>">Edit</td>
                        <td><a href="<?php echo route('maid/delete', $maid['maid_id']); ?>" onclick="return confirmation();">Delete</td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    function confirmation() {
        return confirm('Do you want to delete this record?');
    }
</script>
