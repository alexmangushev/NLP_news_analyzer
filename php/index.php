<?php require_once 'header.php';?>
<?php
require __DIR__.'/vendor/autoload.php'; // include Composer's autoloader

$client = new MongoDB\Client("mongodb://localhost:27017");
$collection = $client->NLP->First;

$result = $collection->find(); //fix /home/alex/nlp/sema/php/vendor/mongodb/mongodb/src/Operation/Find.php:317

$start_index = 0;
$step = 10;

// get count of data in data base
$count_of_record = 0;
foreach($result as $item)
    $count_of_record++;

$result = $collection->find(); //fix /home/alex/nlp/sema/php/vendor/mongodb/mongodb/src/Operation/Find.php:317


//print_r($count_of_record);

if (!empty($_GET))
{
    $start_index = $_GET['count'];

    if ($start_index < 0)
        $start_index = 0;
    elseif (($start_index + $step) > $count_of_record) 
        $start_index = $count_of_record - $step;


    // Поиск записи по ID
    if (sizeof($_GET['id']) > 0)
    {
        $step = 1;
        $result = $collection->find(); //fix /home/alex/nlp/sema/php/vendor/mongodb/mongodb/src/Operation/Find.php:317
        

        $i = 0;
        foreach($result as $item)
        {
            if ($item['_id'] == $_GET['id'])
                $start_index = $i;
            $i++;
        }

        $result = $collection->find(); //fix /home/alex/nlp/sema/php/vendor/mongodb/mongodb/src/Operation/Find.php:317
        
    }
    
}

?>

<div class="container">
    <p class="py-2"> <a href="/php/second.php">Второй студент</a></p>
    <p class="py-2"> <a href="/php/third.php">Третий студент</a></p>
</div>

<!-- db data 1 -->
<div class="container">
    
    <p class="py-2"> Общее число записей: <?php print_r($count_of_record) ?></p>

    <form action="index.php" method="GET">
        <div class="col-md-12 text-center ">
            <div class="form-group">
                <input type="text" name="id" id="id" class="form-control" placeholder="63a0eb6fcc623a5f6f506214 ">
                <button type="submit" class=" btn btn-block mybtn btn-primary tx-tfm login-btn">Поиск</button>
            </div>
        </div>
    </form>

    <form action="index.php" method="GET">
        <div class="col-md-12 text-center ">
            <div class="form-group">
                <button type="submit" class=" btn btn-block mybtn btn-primary tx-tfm login-btn">Отмена</button>
            </div>
        </div>
    </form>

    <div class="container text-center mt-3">
    <?php if(count($result) > 0):?>
            <table class="table">
                <thead>
                <tr>
                    <th scope="col">Номер</th>
                    <th scope="col">ID</th>
                    <th scope="col">Название</th>
                    <th scope="col">Дата</th>
                    <th scope="col">Ссылка</th>
                    <th scope="col">Текст</th>
                </tr>
                </thead>

                <tbody>
                <?php $cnt = 0; foreach($result as $item):?>
                    <tr>
                        <?php if ($cnt >= $start_index && $cnt < $start_index + $step):?>
                            <td><?php print_r($cnt) ?></td>
                            <td><?php print_r($item['_id']) ?></td>
                            <td><?php print_r($item['news_name']) ?></td>
                            <td><?php print_r($item['date']) ?></td>
                            <td><?php print_r($item['link']) ?></td>
                            <td><?php print_r($item['text']) ?></td>
                        <?php endif;?>
                <?php $cnt++; endforeach;?>
                </tbody>
            </table>
    <?php endif;?>
    </div>

</div>

<form action="index.php" method="GET">

    <div class="col-md-12 text-center ">
        <div class="form-group">
            <input type="text" hidden name="count" id="count" value="<?php print_r($start_index - $step) ?>"
             class="form-control">
            <button type="submit" class=" btn btn-block mybtn btn-primary tx-tfm login-btn">Назад</button>
        </div>
    </div>
</form>

<form action="index.php" method="GET">

    <div class="col-md-12 text-center ">
        <div class="form-group">
            <input type="text" hidden name="count" id="count" value="<?php print_r($start_index + $step) ?>" 
            class="form-control">
            <button type="submit" class=" btn btn-block mybtn btn-primary tx-tfm login-btn">Вперед</button>
        </div>
    </div>
</form>

</body>
</html>