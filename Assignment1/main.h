#define MAX_PRIME 1000000000000

typedef struct
{
    int a;   /** First prime */
    int b;   /** Second prime */
    int gap; /** Gap between the two primes */

    int smallest; /** Smallest prime in the range */
    int largest;  /** Largest prime in the range */
} RangeInformation;
