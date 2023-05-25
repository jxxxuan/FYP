<?php
$database = new Database();
$orders = $database->table('booking')->rows();
$flash = getFlash('message');
?>

<div class="order-view-container">
    <div class="order-view-left ml-3">
        <?php require_once getView('admin.menu'); ?>
    </div>

    <div class="order-view-right mr-3 pb-3 text-center">
        <h2>ORDER LIST</h2>
        <table class="order-view-table" border="1">
            <thead>
                <tr>
                    <th>Order ID</th>
                    <th>Member ID</th>
                    <th>Member Name</th>
                    <th>Member Gender</th>
                    <th>T-Shirt Size</th>
                </tr>
            </thead>

            <tbody>
                <?php foreach ($orders as $order) : ?>
                    <?php $member = $database->table('member')->where('member_id', $order['member_id'])->row(); ?>
                    <tr>
                        <td><?php echo $order['order_id']; ?></td>
                        <td><?php echo $order['member_id']; ?></td>
                        <td><?php echo $member['member_name']; ?></td>
                        <td><?php echo $member['member_gender']; ?></td>
                        <td><?php echo $order['member_t_size']; ?></td>
                        <td><a href="<?php echo route('order/edit', $order['order_id']); ?>">Edit</td>
                        <td><a href="<?php echo route('order/delete', $order['order_id']); ?>" onclick="return confirmation();">Delete</td>
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