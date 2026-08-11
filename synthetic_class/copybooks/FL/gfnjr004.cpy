******************************************************************
*  COPYBOOK  : GFNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NJ
******************************************************************
 01  RT-FNJ-RATING.

          03 RT-FNJ-TERRITORY-CODE            PIC X(3).
          03 RT-FNJ-CLASS-CODE                PIC X(4).
          03 RT-FNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNJ-RATED-PREMIUM             PIC 9(9)V9(2).
