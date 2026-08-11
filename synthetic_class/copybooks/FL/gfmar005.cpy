******************************************************************
*  COPYBOOK  : GFMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MA
******************************************************************
 01  RT-FMA-RATING.

          03 RT-FMA-TERRITORY-CODE            PIC X(3).
          03 RT-FMA-CLASS-CODE                PIC X(4).
          03 RT-FMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMA-RATED-PREMIUM             PIC 9(9)V9(2).
