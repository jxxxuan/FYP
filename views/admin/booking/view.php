<?php
$database = new Database();
$bookings = $database->table('booking')->rows();
$flash = getFlash('message');
?>

<div class="booking-view-container">
    <div class="booking-view-left ml-3">
        <?php require_once getView('admin.menu'); ?>
    </div>

    <div class="booking-view-right mr-3 pb-3 text-center">
        <h2>BOOKING LIST</h2>
        <table class="booking-view-table" border="1">
            <thead>
                <tr>
                    <th>Booking ID</th>
                    <th>Service ID</th>
                    <th>Member ID</th>
                    <th>Maid ID</th>
                    <th>Booking Date Time</th>
                    <th>Booking Status</th>
                    <th>Booking Arrive Time</th>
                    <th>Booking Address</th>
                </tr>
            </thead>

            <tbody>
                <?php foreach ($bookings as $booking) : ?>
                    <?php 
                        $service = $database->table('service')->where('service_id', $booking['service_id'])->row();
                        $member = $database->table('member')->where('member_id', $booking['member_id'])->row();
                        $maid = $database->table('maid')->where('maid_id', $booking['maid_id'])->row();
                    ?>
                    <tr>
                        <td><?php echo $booking['booking_id']; ?></td>
                        <td><?php echo $service['service_id']; ?></td>
                        <td><?php echo $member['member_id']; ?></td>
                        <td><?php echo $maid['maid_id']; ?></td>
                        <td><?php echo $booking['booking_date_time']; ?></td>
                        <td><?php echo $booking['booking_status']; ?></td>
                        <td><?php echo $booking['booking_arrive_time']; ?></td>
                        <td><?php echo $booking['booking_address']; ?></td>
                        <td><a href="<?php echo route('booking/edit', $booking['booking_id']); ?>">Edit</td>
                        <td><a href="<?php echo route('booking/delete', $booking['booking_id']); ?>" onclick="return confirmation();">Delete</td>
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
