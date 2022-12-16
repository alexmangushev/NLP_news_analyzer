<?php require_once 'header.php';?>
<?php
require_once 'header.php';
require __DIR__.'/vendor/autoload.php'; // include Composer's autoloader

$client = new MongoDB\Client("mongodb://localhost:27017");
$collection = $client->NLP->First;

$result = $collection->find(); //fix /home/alex/nlp/sema/php/vendor/mongodb/mongodb/src/Operation/Find.php:317

/*foreach ($result as $i)
{
    //echo $i['text'] . "\n";
}*/

?>

<div class="container">
    <p class="py-2"> <a href="/php/second.php">Второй студент</a></p>
    <p class="py-2"> <a href="/php/third.php">Третий студент</a></p>
</div>

<!-- db data 1 -->
<div class="container">

    <div class="container text-center mt-3">
    <?php if(count($result) > 0):?>
            <table class="table">
                <thead>
                <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Название</th>
                    <th scope="col">Дата</th>
                    <th scope="col">Ссылка</th>
                    <th scope="col">Текст</th>
                </tr>
                </thead>

                <tbody>
                <?php foreach($result as $item):?>
                    <tr>
                        <td><?php print_r($item['_id']) ?></td>
                        <td><?php print_r($item['news_name']) ?></td>
                        <td><?php print_r($item['date']) ?></td>
                        <td><?php print_r($item['link']) ?></td>
                        <td><?php print_r($item['text']) ?></td>
                <?php endforeach;?>
                </tbody>
            </table>
    <?php endif;?>
    </div>

</div>

</body>
</html>