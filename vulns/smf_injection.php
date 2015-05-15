<?php

require_once(dirname(__FILE__) . '/SSI.php');

function inject_doinject() 
{
    // Ugh. I need to learn a bit more php is this pretty ugly.
    if (isset($_GET['inline']) || isset($_GET['inject']) ||
        isset($_GET['unionstr']) || isset($_GET['unionint']) ||
        isset($_GET['unionstr2']) || isset($_GET['unioninti2']))
    {
        global $smcFunc;
        if (isset($_GET['inline']))
            $query = $_GET['inline'];
        elseif (isset($_GET['inject']))
            $query = "select real_name from smf_members where id_member='" . $_GET['inject'] . "'";
        elseif (isset($_GET['unionstr']))
            $query = "select real_name from smf_members where id_member='" . $_GET['unionstr'] . "'";
        elseif (isset($_GET['unionstr2']))
            $query = "select real_name,usertitle from smf_members where id_member='" . $_GET['unionstr2'] . "'";
        elseif (isset($_GET['unionint']))
            $query = "select id_group from smf_members where id_member='" . $_GET['unionint'] . "'";
        elseif (isset($_GET['unionint2']))
            $query = "select id_group,posts from smf_members where id_member='" . $_GET['unionint2'] . "'";
        else  # should not happen.
            return; 

        $query = htmlspecialchars_decode($query, ENT_QUOTES);
        $result = $smcFunc['db_query']('', $query);


        if (!isset($_GET['blind'])) 
        {
            echo "<div id=\"injection\">";
            echo "<div id=\"query\">$query</div>";

            ob_start();
            var_dump($result);
            $raw_result = ob_get_clean();

            echo "<div id=\"injection-raw-result\">$raw_result</div>";

            echo "<div id=\"injection-result\">"; 
            echo '<table border="1">';
            while ($row = $smcFunc['db_fetch_assoc']($result))
            {
                echo "<tr>";
                foreach ($row as $key => $value) 
                    echo "<td>$key : $value</td>";
                echo "</tr>"; 
            }
            echo "</table>";
            echo "</div>"; 
        }
        $smcFunc['db_free_result']($result);
    }
}

?>
