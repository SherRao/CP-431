#include <stdio.h>
#include <mpi.h>
#include <stdbool.h>
#include <string.h>

int IsPrime(int n);

int main(int argc, char **argv)
{

    int x =0;
    x += IsPrime(1000003);
    
    printf("%d +++", x);

    return 0;
}

int IsPrime(int n)
{
    int x = 0;

    if (n == 2 || n == 3)
        return true;

    if (n <= 1 || n % 2 == 0 || n % 3 == 0)
        return false;

    for (int i = 5; i * i <= n; i += 6)
    {
        x++;
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    
    return x;
}
