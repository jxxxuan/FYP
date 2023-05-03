<?php 
// Create a new instance of the database class
$db = new Database();

// Set the table to the bookings table
$db->table('booking');

// Set the where clause to get only bookings for the logged in maid
$db->where('maid_id', getSession('id'));
// Get the bookings for the maid
$bookings = $db->rows();

// Check if the form has been submitted
if (isPostMethod()) {
    // Loop through each booking and update the confirmation status
    foreach ($bookings as $booking) {
        $id = $booking['booking_id'];

        if (isset($_POST['accept'][$id])) {
            $db->where('booking_id', $id)->update(['booking_status' => 'accept']);
        }
        elseif (isset($_POST['reject'][$id])) {
            $db->where('booking_id', $id)->update(['booking_status' => 'reject']);
        }
    }

    // Refresh the page to show the updated confirmation status
    header('Location: ' . $_SERVER['REQUEST_URI']);
    exit();
} 
?>

<head>
    <title>My Bookings</title>
</head>
<body>
    <h1>My Bookings</h1>
    <?php
		$db = new Database();
		$bookings = db->where('maid_id',getSession('id'))
	?>
    <table>
        <thead>
            <tr>
                <th>Arrived Date</th>
                <th>Confirmed</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($bookings as $booking) : ?>
            <tr>
                <td><?= $booking['booking_arrive_time'] ?></td>
                <td>
                    <form method="post">
                        <input type="hidden" name="id" value="<?= $booking['booking_id'] ?>">
                        <?php if ($booking['booking_status']) : ?>
                            <input type="submit" name="accept[<?= $booking['booking_id'] ?>]" value="Accept">
                        <?php else : ?>
                            <input type="submit" name="reject[<?= $booking['booking_id'] ?>]" value="Reject">
                        <?php endif; ?>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</body>



