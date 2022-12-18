<?php require_once 'header.php';?>

<div class="container">
    <p class="py-2"> <a href="/php/index.php">Первый студент</a></p>
    <p class="py-2"> <a href="/php/second.php">Второй студент</a></p>
    <p class="py-2"> <a href="/php/third.php">Третий студент</a></p>
</div>

<?php
if (!empty($_GET))
{
    $scrypt_ind = $_GET['scrypt'];

    if ($scrypt_ind == 1) //парсинг
    {
        
    }
    elseif ($scrypt_ind == 2) //обработка данных
    {

    }
    elseif ($scrypt_ind == 3) //анализ тональности
    {
        
    }
}
?>