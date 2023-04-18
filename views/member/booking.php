<!DOCTYPE html>
<html>
<head>
	<title>Confirm Booking</title>
	<style>
		.container {
			max-width: 1200px;
			margin: 0 auto;
			padding: 20px;
		}

		.section {
			margin-bottom: 20px;
		}

		.section h2 {
			margin-bottom: 10px;
		}

		.section table {
			width: 100%;
			border-collapse: collapse;
		}

		.section table th,
		.section table td {
			padding: 10px;
			text-align: left;
			border: 1px solid #ddd;
		}

		.section table th {
			background-color: #f2f2f2;
		}

		.button {
			display: inline-block;
			padding: 10px 20px;
			background-color: #4CAF50;
			color: #fff;
			text-decoration: none;
			border-radius: 5px;
			font-size: 16px;
			margin-top: 20px;
		}
	</style>
</head>
<body>
	<div class="container">
		<h1>Confirm Booking</h1>
		<div class="section">
			<h2>Selected Service Plan</h2>
			<table>
				<thead>
					<tr>
						<th>Title</th>
						<th>Type</th>
						<th>Description</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>{service_title}</td>
						<td>{service_type}</td>
						<td>{service_description}</td>
					</tr>
				</tbody>
			</table>
		</div>
		<div class="section">
			<h2>Selected Maid</h2>
			<table>
				<thead>
					<tr>
						<th>Name</th>
						<th>Age</th>
						<th>Gender</th>
						<th>Contact</th>
						<th>Skill</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>{maid_name}</td>
						<td>{maid_age}</td>
						<td>{maid_gender}</td>
						<td>{maid_contact}</td>
						<td>{maid_skill}</td>
					</tr>
				</tbody>
			</table>
		</div>
		<a href="#" class="button">Confirm Booking</a>
	</div>
</body>
</html>
