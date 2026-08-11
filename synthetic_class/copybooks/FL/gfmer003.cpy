******************************************************************
*  COPYBOOK  : GFMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : ME
******************************************************************
 01  RT-FME-RATING.

          03 RT-FME-TERRITORY-CODE            PIC X(3).
          03 RT-FME-CLASS-CODE                PIC X(4).
          03 RT-FME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FME-RATED-PREMIUM             PIC 9(9)V9(2).
