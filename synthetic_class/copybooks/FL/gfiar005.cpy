******************************************************************
*  COPYBOOK  : GFIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : IA
******************************************************************
 01  RT-FIA-RATING.

          03 RT-FIA-TERRITORY-CODE            PIC X(3).
          03 RT-FIA-CLASS-CODE                PIC X(4).
          03 RT-FIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FIA-RATED-PREMIUM             PIC 9(9)V9(2).
