<?php

class Database
{
    /**
     * Database connection
     *
     * @var mysqli
     */
    protected $connection = null;

    /**
     * Table name
     *
     * @var string
     */
    protected $table = '';

    /**
     * Where query data
     *
     * @var array
     */
    protected $wheres = [];

    /**
     * Indicate prepare function is used
     *
     * @var boolean
     */
    protected $prepared = false;

    /**
     * Initialize database connection
     *
     * @var mysqli_result
     */
    protected $result = null;

    public function __construct()
    {
        $this->connection = mysqli_connect('localhost', 'root', 'root', 'maid_booking');
    }

    public function __destruct()
    {
        if ($this->result !== null) {
            $this->result->free();
        }
        mysqli_close($this->connection);
    }

    /**
     * Process query where statement
     *
     * @param array $where
     * @return string
     */
    protected function processWhere($where = [])
    {
        if (!empty($where)) {
            $this->wheres[] = $where;
        }

        return implode('AND ', array_map(function ($where) {
            $value = $where[1];

            if (is_string($value)) {
                $value = "'{$this->connection->escape_string($value)}'";
            }

            return "`$where[0]` = $value";
        }, $this->wheres));
    }

    /**
     * Prepare query result
     *
     * @param array|string $columns
     * @param bool $return
     * @return mysqli_result|Database
     */
    public function prepare($columns = '*', $return = false)
    {
        $select = $columns === '*'
            ? '*'
            : implode(
                ', ',
                array_map(function ($column) {
                    return "`$column`";
                }, $columns)
            );

        $query = "SELECT $select FROM `$this->table`";
        if (isset($this->wheres[0])) {
            $query .= " WHERE {$this->processWhere()};";
        }

        $result = $this->connection->query($query);

        if ($return) {
            return $result;
        }

        $this->prepared = true;
        $this->result = $result;

        return $this;
    }

    /**
     * Reset query variables
     *
     * @return never
     */
    protected function reset()
    {
        $this->table = '';
        $this->wheres = [];
        $this->prepared = false;
    }

    /**
     * Set table name
     *
     * @param string $table
     * @return Database
     */
    public function table($table)
    {
        $this->table = $table;

        return $this;
    }

    /**
     * Insert record and return last id
     *
     * @param array $data
     * @return int
     */
    public function insert($data)
    {
        $columns = implode(
            ', ',
            array_map(function ($column) {
                return "`$column`";
            }, array_keys($data))
        );
        $values = implode(
            ', ',
            array_map(function ($value) {
                if (is_string($value)) {
                    return "'{$this->connection->escape_string($value)}'";
                }

                return $value;
            }, array_values($data))
        );

        $this->connection->query("INSERT INTO `$this->table` ($columns) VALUES ($values);");
		$last_id = $this->connection->insert_id;

        $this->reset();

        return $last_id;
    }

    /**
     * Update record
     *
     * @param array $data
     * @return bool
     */
    public function update($data)
    {
        $sets = [];
        foreach ($data as $column => $value) {
            if (is_string($value)) {
                $value = "'{$this->connection->escape_string($value)}'";
            }

            $sets[] = "`$column` = $value";
        }
        $set = implode(', ', $sets);

        $result = $this->connection->query("UPDATE `$this->table` SET $set WHERE {$this->processWhere()};");

        $this->reset();

        return $result;
    }

    /**
     * Delete record
     *
     * @return bool
     */
    public function delete()
    {
        $result = $this->connection->query("DELETE FROM `$this->table` WHERE {$this->processWhere()};");

        $this->reset();

        return $result;
    }

    /**
     * Get list of associate data
     *
     * @param string $columns
     * @return array
     */
    public function rows($columns = '*')
    {
        $result = $this->result ?? $this->prepare($columns, true);

        if (!$this->prepared) {
            $this->reset();
        }

        return $result->fetch_all(MYSQLI_ASSOC);
    }

    /**
     * Get row of associate data
     *
     * @param string $columns
     * @return array|null
     */
    public function row($columns = '*')
    {
        $result = $this->result ?? $this->prepare($columns, true);

        if (!$this->prepared) {
            $this->reset();
        }

        return $result->fetch_assoc();
    }

    /**
     * Get number of rows
     *
     * @param array|string $columns
     * @return int|string
     */
    public function numRows($columns = '*')
    {
        $result = $this->result ?? $this->prepare($columns, true);

        if (!$this->prepared) {
            $this->reset();
        }

        return $result->num_rows;
    }

    /**
     * Set where variable
     *
     * @param string $column
     * @param float|int|string $value
     * @return Database
     */
    public function where($column, $value)
    {
        $this->wheres[] = [$column, $value];

        return $this;
    }
	
}
