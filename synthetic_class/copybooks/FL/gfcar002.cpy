******************************************************************
*  COPYBOOK  : GFCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : CA
******************************************************************
 01  RT-FCA-RATING.

          03 RT-FCA-TERRITORY-CODE            PIC X(3).
          03 RT-FCA-CLASS-CODE                PIC X(4).
          03 RT-FCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FCA-RATED-PREMIUM             PIC 9(9)V9(2).
