<?php
if (!authenticated(ADMIN_ROLE)) {
    redirect('authentication/sign-in');
}

$db = new Database();
$ratings = $db->table('rating')->rows();
$flash = getFlash('message');

if(count($ratings) > 0){
?>
	<h2>RATING LIST</h2>
	<table class="admin-table box" style="min-width:97%">
		<thead>
			<tr>
				<th>Rating ID</th>
				<th>Member ID</th>
				<th>Maid ID</th>
				<th>Rating Score</th>
				<th>Comment</th>
			</tr>
		</thead>

		<tbody>
			<?php foreach ($ratings as $rating) { ?>
				<tr>
					<td><?php echo $rating['rating_id']; ?></td>
					<td><a href=<?php echo route('member/member_profile',$rating['member_id'])?>><?php echo $rating['member_id']; ?></a></td>
                    <td><a href=<?php echo route('maid/maid_profile?maid_id='.$rating['maid_id'])?>><?php echo $rating['maid_id']; ?></td>
                    <td><?php echo $rating['rating_score']; ?></td>
                    <td><?php echo $rating['comment']; ?></td>

                    <td><a href="<?php echo route('admin/rating/delete', $rating['rating_id']); ?>" onclick="return confirmation();">Delete</a></td>

				</tr>
			<?php } ?>
		</tbody>
	</table>
<?php
}else{
?>
	<h2 class='box text-center'>No Rating found</h2>
<?php
}
?>

<script>
    <?php if ($flash !== null) : ?>
        alert('<?php echo $flash; ?>');
    <?php endif; ?>

    function confirmation() {
        return confirm('Do you want to delete this record?');
    }
</script>
