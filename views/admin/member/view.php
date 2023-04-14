<?php
$database = new Database();
$members = $database->table('member')->rows();
$flash = getFlash('message');
?>

<div class="member-view-container">
    <div class="member-view-left ml-3">
        <?php require_once getView('admin.menu'); ?>
    </div>

    <div class="member-view-right mr-3 pb-3 text-center">
        <h2>MEMBER LIST</h2>
        <table class="member-view-table" border="1">
            <thead>
                <tr>
                    <th>Member ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Contact</th>
                    <th>Address</th>
                    <th>Image</th>
                </tr>
            </thead>

            <tbody>
                <?php foreach ($members as $member) : ?>
                    <tr>
                        <td><?php echo $member['member_id']; ?></td>
                        <td><?php echo $member['member_username']; ?></td>
                        <td><?php echo $member['member_email']; ?></td>
                        <td><?php echo $member['member_contact']; ?></td>
                        <td><?php echo $member['member_address']; ?></td>
                        <td><img src="<?php echo asset('' . $member['member_image_file_path']); ?>" alt="Member Image" style="height:150px;width:150px;"></td>
                        <td><a href="<?php echo route('member/edit', $member['member_id']); ?>">Edit</td>
                        <td><a href="<?php echo route('member/delete', $member['member_id']); ?>" onclick="return confirmation();">Delete</td>
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
